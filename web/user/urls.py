# acounts/urls.py
from django.urls import path
from . import views # the “.” means current directory
urlpatterns = [
    path('register/', views.register, name='register'),
]