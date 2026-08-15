"""Authentication forms: signup with full name, login with username + email + password."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User


class SignupForm(forms.ModelForm):
    """Registration: username, email, full name and password."""

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
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    # ترتیب نمایش فیلدها (پسوردها آخر)
    field_order = ("username", "email", "first_name", "last_name", "password1", "password2")

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
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Login requires all three: username + email + password."""

    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        password = cleaned.get("password")
        if not (username and email and password):
            return cleaned
        try:
            user = User.objects.get(username__iexact=username, email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_("Invalid username, email or password."))
        if not user.check_password(password):
            raise forms.ValidationError(_("Invalid username, email or password."))
        self.user = user
        return cleaned

    def get_user(self):
        return getattr(self, "user", None)