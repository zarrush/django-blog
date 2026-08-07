from django.db import models
from django.utils import timezone 
from django.contrib.auth.models import User 
from django.urls import reverse

from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id, self.slug])  

class Post(models.Model): 
    # Status eligible for publication.
    class Status(models.TextChoices): 
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
    #  Manage the only PUBLISHED Posts.
    class PublishedManager(models.Manager): 
        def get_queryset(self):
            return super().get_queryset()\
                    .filter(status = Post.Status.PUBLISHED)
    
    title = models.CharField(max_length=250) 
    slug = models.SlugField(max_length=250,unique_for_date='publish') 
    body = models.TextField() 
    publish = models.DateTimeField(default= timezone.now) 
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 
    # One-to-many relationship (if the author is deleted, their posts are also deleted)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts') 
    status = models.CharField(max_length=2,choices=Status.choices,default=Status.DRAFT)
    categories = models.ManyToManyField(Category,related_name='posts',blank=True)
    # Managers
    objects = models.Manager() 
    published = PublishedManager() 
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    tags = TaggableManager() # Tagging

    class Meta:
        # Show the most recently published posts first.
        ordering =['-publish'] 
        # Speed up database queries that filter or sort by publication date.
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title 

    def get_absolute_url(self):
        # Generate the canonical URL for this post using its publication date and slug.
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ],
)
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post= models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_like')
        ]
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user} → {self.post}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete= models.CASCADE, related_name= 'comments')
    name= models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created'])]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
