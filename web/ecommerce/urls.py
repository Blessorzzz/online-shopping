from django.urls import path
from . import views # the “.” means current directory
urlpatterns = [
 path('', views.home.as_view(), name='home'),
 ]