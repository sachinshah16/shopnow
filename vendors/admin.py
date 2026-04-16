from django.contrib import admin
from .models import Vendor, Shop


class ShopInline(admin.TabularInline):
    model = Shop
    extra = 0


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['business_name', 'user__username', 'user__email']
    inlines = [ShopInline]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'shop_type', 'city', 'rating', 'is_active', 'created_at']
    list_filter = ['shop_type', 'is_active', 'city']
    search_fields = ['name', 'vendor__business_name', 'city']
