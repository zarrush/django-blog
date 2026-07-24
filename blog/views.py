from django.shortcuts import render,get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import CommentForm
from django.views.decorators.http import require_POST
# نمایش لیست تمام پست‌های منتشرشده
def post_list(request):
    post_list = Post.published.all() # دریافت فقط پست‌هایی که وضعیت آن‌ها Published است
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)   
    except PageNotAnInteger:
        posts = paginator.page(paginator.num_pages)
    except EmptyPage:
        posts = paginator.page(1)     

    return render(request, # ارسال لیست پست‌ها به قالب برای نمایش
                    'blog/post/list.html',
                    {'posts': posts})
# نمایش جزئیات یک پست بر اساس شناسه (id)
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
                                Post, # دریافت پست موردنظر؛ در صورت پیدا نشدن، خطای 404 نمایش داده می‌شود
                                status= Post.Status.PUBLISHED,
                                slug= post,
                                publish__year= year,
                                publish__month= month,
                                publish__day= day
                            )
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, # ارسال اطلاعات پست به قالب جزئیات
                    'blog/post/detail.html',
                    {'post': post,
                    'comments': comments,
                    'form': form})
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                                id=post_id,
                                status=Post.Status.PUBLISHED)
    comment=None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return render(request,
                        'blog/post/comment.html',
                        {
                            'post':post,
                            'form':form,
                            'comment':comment
                        })