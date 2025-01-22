# ecommerce/views.py
from django.shortcuts import render
from django.views.generic import ListView
from .models import Product
class home(ListView):
    model= Product
    template_name='home.html'
    