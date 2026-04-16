from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('dashboard/', views.VendorDashboardView.as_view(), name='dashboard'),
    path('shop/create/', views.ShopCreateView.as_view(), name='shop_create'),
    path('shop/<int:pk>/edit/', views.ShopUpdateView.as_view(), name='shop_edit'),
    path('products/', views.VendorProductListView.as_view(), name='products'),
    path('products/add/', views.VendorProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.VendorProductEditView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.VendorProductDeleteView.as_view(), name='product_delete'),
    path('orders/', views.VendorOrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.VendorOrderDetailView.as_view(), name='order_detail'),
    path('variants/<int:pk>/delete/', views.VendorVariantDeleteView.as_view(), name='variant_delete'),
    path('images/<int:pk>/delete/', views.VendorImageDeleteView.as_view(), name='image_delete'),
    path('api/quick-sell/', views.VendorQuickSellAPIView.as_view(), name='api_quick_sell'),
]
