from django.contrib import admin
from .models import ForumPost, Comment, ReportedComment

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'forum_post', 'author', 'content', 'created_at', 'report_count')
    list_filter = ('created_at', 'reports')  # Add a filter for reported comments
    search_fields = ('content', 'author__username', 'forum_post__title')  # Allow searching by content, author, or post title

    def report_count(self, obj):
        """Display the number of reports for a comment."""
        return len(obj.reports)
    report_count.short_description = 'Report Count'

class ReportedCommentAdmin(admin.ModelAdmin):
    """
    Admin class to display only reported comments.
    """
    list_display = ('id', 'forum_post', 'author', 'content', 'created_at', 'report_count')
    list_filter = ('created_at',)  # Filter by creation date
    search_fields = ('content', 'author__username', 'forum_post__title')  # Allow searching by content, author, or post title

    def get_queryset(self, request):
        """
        Override the default queryset to show only reported comments.
        """
        queryset = super().get_queryset(request)
        return queryset.exclude(reports=[]).distinct()  # Exclude comments with an empty reports field

    def report_count(self, obj):
        """Display the number of reports for a comment."""
        return len(obj.reports)
    report_count.short_description = 'Report Count'

class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'product')
    list_filter = ('created_at', 'product')
    search_fields = ('title', 'author__username', 'product__product_name')

admin.site.register(ForumPost, ForumPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportedComment, ReportedCommentAdmin)  # Register the proxy model