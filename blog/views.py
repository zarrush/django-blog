from django.shortcuts import render,get_object_or_404
from .models import Post
# نمایش لیست تمام پست‌های منتشرشده
def post_list(request):
    posts = Post.published.all() # دریافت فقط پست‌هایی که وضعیت آن‌ها Published است
    return render(request, # ارسال لیست پست‌ها به قالب برای نمایش
                    'blog/post/list.html',
                    {'posts': posts})
# نمایش جزئیات یک پست بر اساس شناسه (id)
def post_detail(request, id):
    post = get_object_or_404(Post, # دریافت پست موردنظر؛ در صورت پیدا نشدن، خطای 404 نمایش داده می‌شود
                            id = id,
                            status = Post.Status.PUBLISHED)
    return render(request, # ارسال اطلاعات پست به قالب جزئیات
                    'blog/post/detail.html',
                    {'post': post})