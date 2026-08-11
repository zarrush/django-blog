import re

from django.conf import settings
from django.shortcuts import redirect


def switch_language(request, lang):
    valid = dict(settings.LANGUAGES)

    next_url = request.GET.get("next") or "/"
    langs = "|".join(valid.keys())
    next_url = re.sub(rf"^/({langs})", "", next_url) or "/"

    if lang in valid:
        next_url = f"/{lang}{next_url}"
        response = redirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response

    return redirect(next_url)