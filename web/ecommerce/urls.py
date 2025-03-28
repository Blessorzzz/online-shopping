from django.urls import path
from .views import HomePageView, ProductDetailView
from django.conf import settings
from django.conf.urls.static import static
from ecommerce import views

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('api/extract-keywords/', views.extract_keywords, name='extract_keywords'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)