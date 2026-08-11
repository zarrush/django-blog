"""
Admin configuration for the blog application.

Customizes the admin for Post, Comment, Category, Like and Profile,
and extends the built-in User admin with a profile inline.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as AuthUser

from .models import Category, Comment, Like, Post, Profile

from modeltranslation.admin import TranslationAdmin


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('created', 'updated', 'active')
    search_fields = ('name', 'email', 'body')
    list_editable = ('active',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'post__title')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')
    search_fields = ('user__username',)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    """Built-in User admin extended with the profile inline."""
    inlines = (ProfileInline,)


admin.site.unregister(AuthUser)
admin.site.register(AuthUser, UserAdmin)