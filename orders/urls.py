from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/quick-add/', views.QuickAddToCartView.as_view(), name='quick_add_to_cart'),
    path('cart/update/<int:pk>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-success/<int:pk>/', views.OrderSuccessView.as_view(), name='order_success'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/cancel/', views.CustomerCancelOrderView.as_view(), name='cancel_order'),
    path('api/pincode-lookup/', views.PincodeLookupView.as_view(), name='pincode_lookup'),
]
