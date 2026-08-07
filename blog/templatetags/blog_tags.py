"""
Custom template tags and filters for the blog application.

Provides a post counter, a reading-time estimator and
sidebar widgets (latest and most commented posts).
"""

import math
import re

from django import template
from django.db.models import Count
from django.utils.html import strip_tags

from ..models import Post

register = template.Library()

WORDS_PER_MINUTE = 200


@register.simple_tag
def total_posts():
    """Return the number of published posts."""
    return Post.published.count()


@register.filter
def reading_time(content):
    """Estimate reading time based on WORDS_PER_MINUTE."""
    text = strip_tags(content)
    words = re.findall(r'\w+', text)
    minutes = max(1, math.ceil(len(words) / WORDS_PER_MINUTE))
    return f'{minutes} min read'


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """Render the latest published posts for the sidebar."""
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """Return the most commented published posts."""
    return (
        Post.published.annotate(total_comments=Count('comments'))
        .order_by('-total_comments')[:count]
    )