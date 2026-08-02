from django.urls import path
from blog.views import *

app_name = 'blog'

urlpatterns = [
    path('', post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', post_list, name='post_list_by_tag' ),
    # Route requests for a post detail page using its publication date and slug.
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail, name='post_detail'),
    path('<int:post_id>', post_comment, name='post_comment'),
]






