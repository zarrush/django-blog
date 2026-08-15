"""Authentication views: signup, login, email confirmation."""
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_http_methods

from .forms import LoginForm, SignupForm
from .models import User


@require_http_methods(["GET", "POST"])
def auth_view(request):
    """Single page with two tabs: Login and Sign Up."""

    # اگر کاربر لاگین هست، ریدایرکت به هوم
    if request.user.is_authenticated:
        return redirect("blog:post_list")

    active_tab = request.GET.get("tab", "login")

    if request.method == "POST":
        if "signup" in request.POST:
            form_signup = SignupForm(request.POST)
            form_login = LoginForm()
            if form_signup.is_valid():
                user = form_signup.save(commit=False)
                user.is_active = False
                user.confirmation_token = secrets.token_urlsafe(32)
                user.save()
                _send_confirmation_email(request, user)
                messages.success(
                    request,
                    _("Check your email to confirm your account."),
                )
                return redirect("accounts:auth")
        else:
            form_signup = SignupForm()
            form_login = LoginForm(data=request.POST)
            if form_login.is_valid():
                user = form_login.get_user()
                if not user.is_active:
                    messages.error(request, _("Please confirm your email first."))
                else:
                    login(request, user)
                    next_url = request.GET.get("next") or reverse("blog:post_list")
                    return redirect(next_url)
    else:
        form_signup = SignupForm()
        form_login = LoginForm()

    return render(
        request,
        "accounts/auth.html",
        {
            "form_signup": form_signup,
            "form_login": form_login,
            "active_tab": active_tab,
        },
    )


@require_GET
def confirm_email(request, token):
    """Activate user account via confirmation token."""
    user = get_object_or_404(User, confirmation_token=token)
    user.is_active = True
    user.confirmation_token = ""
    user.save(update_fields=["is_active", "confirmation_token"])
    messages.success(request, _("Email confirmed. You can now log in."))
    return redirect("accounts:auth")


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """Log out the current user."""
    from django.contrib.auth import logout

    logout(request)
    return redirect("blog:post_list")


def _send_confirmation_email(request, user):
    """Send email confirmation link to the user."""
    confirm_url = request.build_absolute_uri(
        reverse("accounts:confirm_email", args=[user.confirmation_token])
    )
    context = {"user": user, "confirm_url": confirm_url}
    subject = _("Confirm your email")
    message = render_to_string("accounts/email_confirmation.txt", context)
    html_message = render_to_string("accounts/email_confirmation.html", context)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )