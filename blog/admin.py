from django.contrib import admin
from blog.models import Like, Post, Comment, Category


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):   
    list_display = ['title', 'slug', 'author', 'publish', 'status'] 
    list_filter = ['status', 'created', 'publish', 'author'] 
    search_fields = ['title', 'body'] 
    prepopulated_fields = {'slug': ('title',)} # auto-generate slug from title
    raw_id_fields = ['author'] # show ID input instead of dropdown for FK
    date_hierarchy = 'publish' 
    ordering = ['status', 'publish'] 

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['created', 'updated', 'active']
    search_fields = ['name', 'email', 'body']
    list_editable = ['active']  # toggle comment approval directly from the list view

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'post__title')
