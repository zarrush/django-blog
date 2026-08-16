"""Accounts URLs: auth page and email confirmation."""
from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
app_name = "accounts"

urlpatterns = [
    path("", views.auth_view, name="auth"),
    path("confirm/<str:token>/", views.confirm_email, name="confirm_email"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password-reset/complete/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("panel/", views.user_panel, name="panel"),
    path("panel/edit/", views.profile_edit, name="profile_edit"),
]


