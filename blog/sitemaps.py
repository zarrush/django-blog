"""Sitemap configuration for the blog application."""

from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    """Expose published posts to search engines."""

    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated