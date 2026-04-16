from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('shops/', views.ShopListView.as_view(), name='shop_list'),
    path('shops/<int:pk>/', views.ShopDetailView.as_view(), name='shop_detail'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('api/variant/', views.GetVariantView.as_view(), name='get_variant'),
    path('api/search-suggest/', views.SearchSuggestView.as_view(), name='search_suggest'),
    path('api/reverse-geocode/', views.ReverseGeocodeView.as_view(), name='reverse_geocode'),
    path('api/geo-search/', views.GeoSearchView.as_view(), name='geo_search'),
]
