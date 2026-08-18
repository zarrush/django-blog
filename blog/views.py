"""
Views for the blog application.

Handles post listing (with tag/category filters), post detail,
comments, likes, search, archive and author pages.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from taggit.models import Tag

from .forms import CommentForm, SearchForm
from .models import Category, Like, Post, Comment

User = get_user_model()

# Constants
POSTS_PER_PAGE = 3
SIMILAR_POSTS_LIMIT = 4
RELATED_POSTS_LIMIT = 3
TRIGRAM_THRESHOLD = 0.1
COMMENTS_PER_HOUR = 3


def get_client_ip(request):
    """Return the client's IP address."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def post_list(request):
    """Blog main page: search (title+tags), popular/latest modes, pagination."""
    q = request.GET.get("q", "").strip()
    mode = request.GET.get("mode", "latest")

    posts = Post.published.all()

    if q:
        posts = posts.filter(
            Q(title__icontains=q) | Q(tags__name__icontains=q)
        ).distinct()

    if mode == "popular":
        posts = (
            posts
            .annotate(n_likes=Count("likes", distinct=True),
                      n_comments=Count("comments", distinct=True))
            .annotate(score=F("n_likes") + F("n_comments"))
            .order_by("-score", "-publish")
        )
    else:
        posts = posts.order_by("-publish")

    paginator = Paginator(posts, 6)
    try:
        page_obj = paginator.page(request.GET.get("page"))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "blog/post/list.html", {
        "page_obj": page_obj,
        "q": q,
        "mode": mode,
    })


def post_detail(request, year, month, day, post):
    """Post page: hero, body, TOC data, author, related, comments."""
    post = get_object_or_404(
        Post, slug=post, status=Post.Status.PUBLISHED,
        publish__year=year, publish__month=month, publish__day=day,
    )

    comments = post.comments.all()
    if hasattr(Comment, "active"):
        comments = comments.filter(active=True)
    sort = request.GET.get("sort", "newest")
    comments = comments.order_by("created" if sort == "oldest" else "-created")

    related = (
        Post.published
        .filter(categories__in=post.categories.all())
        .exclude(id=post.id)
        .distinct()[:3]
    )

    reading_time = max(1, round(len(post.body.split()) / 200))

    return render(request, "blog/post/detail.html", {
        "post": post,
        "comments": comments,
        "sort": sort,
        "related": related,
        "reading_time": reading_time,
    })


@login_required
@require_POST
def post_like(request, post_id):
    """Toggle a like on a post for the logged-in user."""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect(post.get_absolute_url())


@require_POST
def post_comment(request, post_id):
    """Create a comment (authenticated or guest) and redirect back."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        honeypot = request.POST.get("website", "")
        if body and not honeypot:
            if request.user.is_authenticated:
                    Comment.objects.create(post=post, author=request.user, body=body)
            else:
                name = request.POST.get("name", "").strip()
                email = request.POST.get("email", "").strip()
                if name and email:
                    Comment.objects.create(post=post, name=name, email=email, body=body)
                else:
                    messages.error(request, "Name and email are required.")
                    return redirect(post.get_absolute_url())
            messages.success(request, "Your comment has been published.")
        else:
            messages.error(request, "Comment could not be submitted.")
    return redirect(post.get_absolute_url())


def post_search(request):
    """Search published posts by title, optionally within a category."""
    form = SearchForm(request.GET or None)
    query = None
    category = None
    results = []

    if form.is_valid():
        query = form.cleaned_data.get("query")
        category = form.cleaned_data.get("category")
        qs = Post.published.select_related('author').prefetch_related('tags', 'categories')
        if category:
            qs = qs.filter(categories=category)
        if query:
            qs = (
                qs.annotate(similarity=TrigramSimilarity('title', query))
                .filter(similarity__gt=TRIGRAM_THRESHOLD)
                .order_by('-similarity')
            )
        elif category:
            qs = qs.order_by('-publish')
        results = qs

    return render(request, 'blog/post/search.html', {
        "form": form, "query": query, "category": category,
        "results": results, "categories": Category.objects.all(),
    })


def post_archive(request):
    """Group published posts by month, newest first."""
    months = Post.published.dates('publish', 'month', order='DESC')
    archive = [
        {
            'period': month_date,
            'posts': Post.published.filter(
                publish__year=month_date.year,
                publish__month=month_date.month,
            ).select_related('author'),
        }
        for month_date in months
    ]
    return render(request, 'blog/post/archive.html', {'archive': archive})


def author_detail(request, username):
    """Public author page: profile + their published posts."""
    author = get_object_or_404(User, username=username)
    posts = Post.published.filter(author=author)
    return render(request, "blog/author.html", {"author": author, "posts": posts})

def post_feedback(request, post_id):
    """One helpful-vote per session."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    key = f"feedback_{post.id}"
    if request.method == "POST" and not request.session.get(key):
        value = request.POST.get("value")
        if value == "yes":
            Post.objects.filter(id=post.id).update(helpful_yes=F("helpful_yes") + 1)
        elif value == "no":
            Post.objects.filter(id=post.id).update(helpful_no=F("helpful_no") + 1)
        request.session[key] = value
        messages.success(request, "Thanks for your feedback!")
    return redirect(post.get_absolute_url())