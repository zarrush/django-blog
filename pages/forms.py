from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
        labels = {
            "name": _("Name"), "email": _("Email"),
            "subject": _("Subject"), "message": _("Message"),
        }