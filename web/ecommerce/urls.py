from django.urls import path
from .views import HomePageView, ProductDetailView,ajax_search_products
from django.conf import settings
from django.conf.urls.static import static
from ecommerce import views

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('api/extract-keywords/', views.extract_keywords, name='extract_keywords'),
    path('api/ajax-search-products/', ajax_search_products, name='ajax_search_products'),
    path('apply-custom-safety-filters/', views.apply_custom_safety_filters, name='apply_custom_safety_filters'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)