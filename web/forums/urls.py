from django.urls import path
from .views import forum_list, forum_detail, create_forum_post, add_comment, select_product_for_forum
from . import views

urlpatterns = [
    path('', forum_list, name='forum_list'),  # Use the imported view directly
    path('<uuid:post_id>/', forum_detail, name='forum_detail'),
    path('select-product/', select_product_for_forum, name='select_product_for_forum'),
    path('create/<uuid:product_id>/', create_forum_post, name='create_forum_post'),
    path('<uuid:post_id>/comment/', add_comment, name='add_comment'),
    path('vote_comment/', views.vote_comment, name='vote_comment'),
    path('report_comment/<int:comment_id>/', views.report_comment, name='report_comment'),
]