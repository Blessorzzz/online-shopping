from django.urls import path
from . import views # the “.” means current directory
from .views import HomePageView, ProductDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)