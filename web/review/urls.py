from django.urls import path
from . import views

urlpatterns = [
    path('add_review/<int:order_id>/', views.add_review, name='add_review'),
    path('my_reviews/', views.my_reviews, name='my_reviews'),
    # Add other URL patterns here
]
