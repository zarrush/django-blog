"""
Views for the blog application.

Handles post listing (with tag/category filters), post detail,
comments, likes, search, archive and author pages.
"""


from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from taggit.models import Tag

from .forms import CommentForm, SearchForm
from .models import Category, Like, Post

User = get_user_model()

# Constants
POSTS_PER_PAGE = 3
SIMILAR_POSTS_LIMIT = 4
RELATED_POSTS_LIMIT = 3
TRIGRAM_THRESHOLD = 0.1


def post_list(request, tag_slug=None, category_slug=None):
    """List published posts, optionally filtered by tag or category."""
    posts = Post.published.select_related('author').prefetch_related('tags', 'categories')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(categories__in=[category])

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'tag': tag,
        'category': category,
    })


def post_detail(request, year, month, day, post):
    """Show a published post with comments, similar and related posts."""
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # Posts sharing the most tags with the current one.
    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = (
        Post.published.filter(tags__in=post_tag_ids)
        .exclude(id=post.id)
        .annotate(same_tags=Count('tags'))
        .order_by('-same_tags', '-publish')[:SIMILAR_POSTS_LIMIT]
    )
    # Posts from the same categories.
    related_posts = (
        Post.published.filter(categories__in=post.categories.all())
        .exclude(id=post.id)
        .order_by('-publish')[:RELATED_POSTS_LIMIT]
    )
    liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
        'related_posts': related_posts,
        'liked': liked,
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
    """Handle a new comment submission on a published post."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    comment = None
    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return render(request, 'blog/post/comment.html', {
            'post': post,
            'form': form,
            'comment': comment,
        })

    # Invalid submissions fall back to the post page.
    return redirect(post.get_absolute_url())


def post_search(request):
    """Search published posts by title using trigram similarity."""
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('title', query),
                )
                .filter(similarity__gt=TRIGRAM_THRESHOLD)
                .order_by('-similarity')
            )

    return render(request, 'blog/post/search.html', {
        'form': form,
        'query': query,
        'results': results,
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
            ),
        }
        for month_date in months
    ]
    return render(request, 'blog/post/archive.html', {'archive': archive})


def author_page(request, username):
    """Show an author's profile info and their published posts."""
    author = get_object_or_404(User, username=username)
    posts = Post.published.filter(author=author)

    return render(request, 'blog/author.html', {
        'author': author,
        'posts': posts,
        'total_posts': posts.count(),
        'total_likes': Like.objects.filter(post__author=author).count(),
    })

