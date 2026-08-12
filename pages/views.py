"""Pages views: home, about, contact."""
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from blog.models import Category, Post

from .forms import ContactForm


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["latest_posts"] = (
            Post.published.select_related("author")
            .prefetch_related("tags", "categories")[:6]
        )
        ctx["categories"] = Category.objects.all()
        return ctx


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contact")

    def form_valid(self, form):
        msg = form.save()
        send_mail(
            f"[Contact] {msg.subject or msg.name}",
            f"{msg.name} <{msg.email}>\n\n{msg.message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
        messages.success(self.request, _("Your message was sent. Thank you!"))
        return super().form_valid(form)