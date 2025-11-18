from django.contrib import admin
from .models import SavedCrossword


@admin.register(SavedCrossword)
class SavedCrosswordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "created_at", "updated_at")
    list_filter = ("category", "created_at")
    search_fields = ("user__username", "category")
