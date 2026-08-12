from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created", "is_read")
    list_filter = ("is_read", "created")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("is_read",)
    readonly_fields = ("name", "email", "subject", "message", "created")