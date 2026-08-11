from modeltranslation.translator import register, TranslationOptions
from .models import Post, Category


@register(Post)
class PostTO(TranslationOptions):
    fields = ("title", "body")   # اگه summary/excerpt داری، اضافه کن


@register(Category)
class CategoryTO(TranslationOptions):
    fields = ("name",)
