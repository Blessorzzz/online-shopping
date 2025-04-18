from django.urls import path
from .views import forum_list, forum_detail, create_forum_post, add_comment
from . import views

urlpatterns = [
    path('<uuid:product_id>/', forum_list, name='forum_list'),
    path('<uuid:product_id>/<uuid:post_id>/', forum_detail, name='forum_detail'),
    path('create/<uuid:product_id>/', create_forum_post, name='create_forum_post'),
    path('<uuid:product_id>/<uuid:post_id>/comment/', views.add_comment, name='add_comment'),
    path('vote_comment/', views.vote_comment, name='vote_comment'),
    path('report_comment/<int:comment_id>/', views.report_comment, name='report_comment'),
]