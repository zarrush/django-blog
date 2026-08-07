"""
Forms for the blog application.

CommentForm handles user comments; SearchForm handles title search.
"""

from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """Form for submitting a comment on a post."""

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    """Simple form for searching posts by title."""

    query = forms.CharField(max_length=100)