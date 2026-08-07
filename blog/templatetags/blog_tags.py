import math
import re
from django import template
from blog.models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from ..models import Post

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.filter
def reading_time(content):
    """
    Estimate reading time based on 200 words per minute.
    """
    text = strip_tags(content)
    words = re.findall(r"\w+", text)
    minutes = max(1, math.ceil(len(words) / 200))
    return f"{minutes} min read"

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag()
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')).order_by('-total_comments')[:count]

