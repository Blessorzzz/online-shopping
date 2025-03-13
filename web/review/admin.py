from django.contrib import admin
from .models import Review
from .forms import ReviewAdminForm

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("user__username", "product__name", "comment")
    actions = ["approve_reviews"]
    form = ReviewAdminForm  # Use the custom admin form

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

admin.site.register(Review, ReviewAdmin)
