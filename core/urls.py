# core/urls.py

"""
URL configuration for the core project.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import set_language

from blog.sitemaps import PostSitemap
from core.views import switch_language


sitemaps = {
    "posts": PostSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),

    # Language switcher (out of i18n — no language prefix)
    path("switch-language/<str:lang>/", switch_language, name="switch_language"),
    path("i18n/setlang/", set_language, name="set_language"),

    # SEO endpoints (also language-less)
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
        ),
        name="robots",
    ),
    
]

urlpatterns += i18n_patterns(
    path("accounts/", include("accounts.urls")),
    path("", include("pages.urls")),        # هوم اول
    path("blog/", include("blog.urls")),    # لیست کامل زیر /blog/
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )