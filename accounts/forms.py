"""Authentication forms: Sign In (identifier+pass), Sign Up (full name first)."""
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import User


class SignupForm(forms.ModelForm):
    """Registration: full name, email, username, password x2."""

    full_name = forms.CharField(
        label=_("Full name"),
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("email", "username")
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
        }

    field_order = ("full_name", "email", "username", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This email is already registered."))
        return email.lower()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Passwords do not match."))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        parts = self.cleaned_data["full_name"].split()
        user.first_name = parts[0] if parts else ""
        user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Sign in with email OR username + password."""

    identifier = forms.CharField(
        label=_("Email or username"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self):
        cleaned = super().clean()
        ident = (cleaned.get("identifier") or "").strip()
        password = cleaned.get("password")
        if not ident or not password:
            return cleaned
        try:
            user = User.objects.get(Q(username__iexact=ident) | Q(email__iexact=ident))
        except User.DoesNotExist:
            raise forms.ValidationError(_("Invalid credentials."))
        if not user.check_password(password):
            raise forms.ValidationError(_("Invalid credentials."))
        self.user = user
        return cleaned

    def get_user(self):
        return getattr(self, "user", None)