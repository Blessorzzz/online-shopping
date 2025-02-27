"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('ecommerce.urls')), 
    path('user/', include('django.contrib.auth.urls')),
    path('user/', include('user.urls')),
    path('shoppingcart/', include('shoppingcart.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('vendor/', include('vendor.urls')),
<<<<<<< HEAD
    path('vendor_login/', include('vendor.urls')),
=======
    path('login/', custom_login, name='login'),
    path('i18n/', include('django.conf.urls.i18n')),
>>>>>>> af3940cc85ffe3432103750a6ded31dad4670790
]



