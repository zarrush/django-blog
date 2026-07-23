from django.contrib import admin
from blog.models import Post,Comment # مادل پست و کامنت
# ستون های سفارشی پنل ادمین
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):   
    list_display = ['title', 'slug', 'author', 'publish', 'status'] # ستون‌هایی که در لیست پست‌ها نمایش داده می‌شوند.
    list_filter = ['status', 'created', 'publish', 'author'] # فیلترهای کنار صفحه ادمین.
    search_fields = ['title', 'body'] # جستجو در title و body.
    prepopulated_fields = {'slug': ('title',)} # با تایپ عنوان، اسلاگ خودکار ساخته می‌شود.
    raw_id_fields = ['author'] # برای ForeignKeyها به جای Select، یک کادر ID نمایش می‌دهد.
    date_hierarchy = 'publish' # بالای صفحه یک ناوبری سال/ماه/روز اضافه می‌کند.
    ordering = ['status', 'publish'] # ترتیب نمایش رکوردها

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['created', 'update', 'active']
    search_fields = ['name', 'email', 'body']