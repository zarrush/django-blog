"""Accounts models: custom User + Profile."""
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager where email is the identifier."""

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    """Custom user: login with email; username kept as optional display name."""

    username = models.CharField(_("username"), max_length=150, blank=True, default="")
    email = models.EmailField(_("email address"), unique=True)

    is_active = models.BooleanField(default=False)  # تا وقتی ایمیل تایید نشه، False
    confirmation_token = models.CharField(max_length=100, blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Extended user profile with bio, avatar and UI preferences."""

    class Theme(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    theme = models.CharField(max_length=10, choices=Theme.choices, blank=True, default="")
    preferred_language = models.CharField(max_length=5, blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_profile(sender, instance, created, **kwargs):
    """Auto-create a Profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()