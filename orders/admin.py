from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Delivery


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_info', 'price', 'subtotal']


class DeliveryInline(admin.StackedInline):
    model = Delivery
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_amount', 'created_at']
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, DeliveryInline]


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'assigned_to', 'status', 'estimated_delivery', 'delivered_at']
    list_filter = ['status']
    search_fields = ['order__order_number', 'assigned_to']
