from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm
from .models import Post


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

    # Render the post detail page with the post, approved comments, and comment form.
    return render(
        request, 
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
)

# Display a paginated list of published blog posts using Django's generic ListView.
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

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