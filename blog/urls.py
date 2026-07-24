from django.urls import path
from blog.views import *
# تعریف فضای نام (namespace) برای آدرس‌های این اپ
app_name = 'blog'
# مسیر های مربوط به اپلکیشن وبلاگ
urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),  # صفحه اصلی وبلاگ(نمایش لیست پست ها)
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
            post_detail,
            name='post_detail'),
    path('<int:post_id>', post_comment, name='post_comment'),
]