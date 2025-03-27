from django.urls import path
from . import views

urlpatterns = [
    path('add_review/<int:order_id>/<uuid:product_id>/', views.add_review, name='add_review'),
    path('my_reviews/', views.my_reviews, name='my_reviews'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('vote_review/', views.vote_review, name='vote_review'),
]
