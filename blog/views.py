from django.shortcuts import render,get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# نمایش لیست تمام پست‌های منتشرشده
def post_list(request):
    post_list = Post.published.all() # دریافت فقط پست‌هایی که وضعیت آن‌ها Published است
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    
    posts = paginator.page(page_number)

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
    return render(request, # ارسال اطلاعات پست به قالب جزئیات
                    'blog/post/detail.html',
                    {'post': post})