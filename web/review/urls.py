from django.urls import path
from .views import add_review, my_reviews

urlpatterns = [
    path("add/<int:order_id>/", add_review, name="add_review"),
    path("my-reviews/", my_reviews, name="my_reviews"),
]