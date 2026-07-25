from django.db import models
from django.utils import timezone # استفاده از زمان فعلی پروژه با در نظر گرفتن مکان فعلی
from django.contrib.auth.models import User # استفاده از مدل پیشفرض جنگو برای ارتباط کاربر و پست
from django.urls import reverse
from taggit.managers import TaggableManager
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
                        .filter(status = Post.Status.PUBLISHED)
    

class Post(models.Model): # تعریف مدل مربوط به پست های وبلاگ
    # تعریف وضعیت های مجاز برای انتشار پست
    class Status(models.TextChoices): 
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length = 250) # عنوان اصلی پست
    slug = models.SlugField(max_length = 250,unique_for_date='publish') # شناسه مناسب برای استفاده در آدرس صفحات 

    body = models.TextField() # محتوای اصلی پست
    # زمان و تاریخ انتشار پست
    publish = models.DateTimeField(default = timezone.now) # زمان انتشار پست
    created = models.DateTimeField(auto_now_add = True) # زمان ایجاد اولیه رکورد
    updated = models.DateTimeField(auto_now = True) # زمان آخرین آپدیت پست
    # هر  پست فقط یک نویسنده داره ولی هر نویسنده چندین پست ONE TO MANY
    author = models.ForeignKey(User,
                                on_delete=models.CASCADE, # اگر نویسنده حذف شود تمام پست هایش حذف میشود
                                related_name='blog_posts') # ایجاد ارتباط بین نویسنده و پست
    # تعیین وضعیت انتشار پست
    status = models.CharField(max_length = 2,
                                choices = Status.choices,
                                default = Status.DRAFT)
    objects = models.Manager() # The default manager
    published = PublishedManager() # our custom manager
    tags = TaggableManager() # Tags
    # اضافه کردن دش به شکل نزولی
        # تعیین ترتیب پیش‌فرض نمایش پست‌ها بر اساس زمان انتشار
    class Meta:
        ordering =['-publish'] # جدیدترین پست ها اول نشان داده شوند
        indexes = [ # ایجاد ایندکس برای افزایش سرعت جستجو و مرتب‌سازی بر اساس زمان انتشار
            models.Index(fields=['-publish']),
        ]
    # مشخص میکند که هر پست با تایتل خودش نشان داده شود نه با شی object
    def __str__(self):
        return self.title # تایتل خودش
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                            args=[self.publish.year,
                                    self.publish.month,
                                    self.publish.day,
                                    self.slug])
    # COMMENTS MODEL
class Comment(models.Model):
    post = models.ForeignKey(Post,
                                on_delete=models.CASCADE,
                                related_name='comments')
    name= models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'