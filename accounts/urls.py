"""Accounts URLs: auth page and email confirmation."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.auth_view, name="auth"),
    path("confirm/<str:token>/", views.confirm_email, name="confirm_email"),
    path("logout/", views.logout_view, name="logout"),
]