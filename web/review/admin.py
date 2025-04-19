from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")  # Removed "is_approved"
    list_filter = ("rating",)  # Removed "is_approved"
    search_fields = ("user__username", "product__name", "comment")
    readonly_fields = ("rating",)  # Make rating read-only in the admin panel

admin.site.register(Review, ReviewAdmin)