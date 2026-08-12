"""
Models for the blog application.

Defines Category, Post, Comment, Like and Profile models with
custom managers, indexes and a signal for auto-creating profiles.
"""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from taggit.managers import TaggableManager


class Category(models.Model):
    """Category for grouping posts."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Links to the list of posts in this category.
        # The corresponding URL pattern will be added in urls.py.
        return reverse('blog:post_list_by_category', args=[self.slug])


class Post(models.Model):
    """A blog post written by an author."""

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    class PublishedManager(models.Manager):
        """Manager that returns only published posts."""
        def get_queryset(self):
            return super().get_queryset().filter(status=Post.Status.PUBLISHED)

    # Fields
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    categories = models.ManyToManyField(
        Category,
        related_name='posts',
        blank=True,
    )
    tags = TaggableManager()

    # Managers
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Generate the canonical URL using publication date and slug."""
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
            ],
        )
    excerpt = models.TextField(
    max_length=300,
    blank=True,
    help_text="Short summary for homepage cards (max 300 chars)",
)
    featured_image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        help_text="Featured image for post cards",
)


class Like(models.Model):
    """A like by a user on a post."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_like',
            ),
        ]

    def __str__(self):
        return f'{self.user} → {self.post}'


class Comment(models.Model):
    """A comment on a blog post."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
