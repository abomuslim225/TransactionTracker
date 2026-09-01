from modeltranslation.translator import register, TranslationOptions
from apps.models import Category


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)