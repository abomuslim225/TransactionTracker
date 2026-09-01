from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import Category, User


# Register your models here.

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'password')
