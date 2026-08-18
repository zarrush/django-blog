"""URL configuration for the blog app."""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Post lists
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('category/<slug:category_slug>/', views.post_list, name='post_list_by_category'),
    path('archive/', views.post_archive, name='post_archive'),
    path('author/<str:username>/', views.author_detail, name='author_page'),
    path('search/', views.post_search, name='post_search'),
    # Post actions
    path('<int:post_id>/like/', views.post_like, name='post_like'),
    path('<int:post_id>/', views.post_comment, name='post_comment'),
    # Post detail (most specific pattern stays last)
    path(
        '<int:year>/<int:month>/<int:day>/<slug:post>/',
        views.post_detail,
        name='post_detail',
    ),
]
