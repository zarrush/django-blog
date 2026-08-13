"""
Forms for the blog application.

CommentForm handles user comments; SearchForm handles title search.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Category, Comment


class CommentForm(forms.ModelForm):
    """Comment form with an invisible honeypot field."""

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "class": "hp-field", "tabindex": "-1",
            "autocomplete": "off", "aria-hidden": "true",
        }),
    )

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    """Search posts by title, optionally filtered by category."""

    query = forms.CharField(
        max_length=100, required=False, label=_("Search"),
        widget=forms.TextInput(attrs={
            "type": "search", "placeholder": _("Search posts..."),
        }),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name="slug",
        required=False,
        label=_("Category"),
    )