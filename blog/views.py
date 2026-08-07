from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import request
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.models import User

from .forms import CommentForm, SearchForm
from django.contrib.postgres.search import TrigramSimilarity

from .models import Post,Like


def post_list(request,tag_slug=None):
    # Retrieve all published blog posts as the base queryset.
    post_list = Post.published.all() 

    tag = None
    if tag_slug:
        # Filter posts by the selected tag when a tag slug is provided.
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Split the queryset into pages with three posts per page.
    paginator = Paginator(post_list, 3)
    # Read the requested page number from the query string.
    page_number = request.GET.get('page', 1)

    try:
        # Return the requested page of results.
        posts = paginator.page(page_number)   
    except PageNotAnInteger:
        # Gracefully fall back to the first page when an invalid page number is provided.
        posts = paginator.page(1)
    except EmptyPage:
        # Return the last available page when the requested page exceeds the valid range
        posts = paginator.page(paginator.num_pages)

    # Render the post listing view with the paginated posts and the active tag filter.
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

# Fetch the requested published post by slug and publication date.
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
)
    # Retrieve only the approved comments associated with the current post.
    comments = post.comments.filter(active=True)
    # Initialize an empty comment form for new user submissions.
    form = CommentForm()

    # List of similar posts
    post_tag_ids = post.tags.values_list('id', flat=True)

    similar_posts = (
        Post.published.filter(tags__in=post_tag_ids)
        .exclude(id=post.id)
        .annotate(same_tags=Count('tags'))
        .order_by('-same_tags', '-publish')[:4]
)
    related_posts = Post.published.filter(
        categories__in=post.categories.all()
    ).exclude(
        id=post.id
    ).order_by(
        "-publish"
    )[:3]
    liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
    # Render the post detail page with the post, approved comments, and comment form.
    return render(
        request, 
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts,
            'related-posts': related_posts,
            'liked': liked,
        },
)

# Display a paginated list of published blog posts using Django's generic ListView.
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

@login_required
@require_POST
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    # 👇 حالا با پارامترهای درست ریدایرکت می‌کنیم
    return redirect('blog:post_detail',
                    year=post.publish.year,
                    month=post.publish.month,
                    day=post.publish.day,
                    post=post.slug)

@require_POST
def post_comment(request, post_id):
    # Retrieve the target published post or return a 404 response if it does not exist.
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )

    # Initialize the comment object and bind the submitted form data.
    comment = None
    form = CommentForm(data=request.POST)

    # Validate and persist the submitted comment.
    if form.is_valid():
        # Create the comment instance without saving it to assign the related post.
        comment = form.save(commit=False)
        # Associate the comment with the current post before saving.
        comment.post = post
        comment.save()

        # Render the confirmation page with the saved comment and related context.
        return render(
            request,
            'blog/post/comment.html',
            {
                'post': post,
                'form': form,
                'comment': comment,
            },
        )

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request,
                    'blog/post/search.html',
                    {'form': form,
                    'query': query,
                    'results': results})

def post_archive(request):
    months = Post.published.dates('publish', 'month', order='DESC')

    archive = []
    for month_date in months:
        posts = Post.published.filter(
            publish__year=month_date.year,
            publish__month=month_date.month
        )
        archive.append({
            'period': month_date,
            'posts': posts,
        })

    return render(request, 'blog/post/archive.html', {
        'archive': archive,
    })

def author_page(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.published.filter(author=author).order_by('-publish')

    return render(request, 'blog/author.html', {
        'author': author,
        'posts': posts,
        'total_posts': posts.count(),
        'total_likes': Like.objects.filter(post__author=author).count(),
    })