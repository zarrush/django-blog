"""
Django settings for the core project.

Development configuration. Sensitive values are read from
environment variables with safe fallbacks for local use.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-%=6-+r=e=nk775_dv!w&v(3oh=i^-j#1mqdtd09qd*@_47#lzk',
)
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Application definition
INSTALLED_APPS = [
    # ترنسلیت
    "modeltranslation",
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',
    # Third-party
    'taggit',
    # Local apps
    'blog',
    'accounts',
    'pages',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",      
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LANGUAGE_CODE = "fa"

LANGUAGES = [
    ("fa", "فارسی"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    "default": ("fa", "en"),   # برای زبان‌هایی که صریح نیومدن (یعنی fa): اول fa، اگه خالی بود en
    "en": ("en", "fa"),        # اگه متن انگلیسی خالی بود → فارسی نشون بده
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "blog" / "templates"],  # ← این خط رو اضافه کن
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mydb'),
        'USER': os.environ.get('POSTGRES_USER', 'myuser'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "blog" / "static",
]
# Will be enabled in the UI phase when global static assets are added:
# STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Sites framework
SITE_ID = 1

# Default primary key type for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

# فقط برای توسعه — لینک تایید رو توی ترمینال چاپ می‌کنه
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@myblog.local"
