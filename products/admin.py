from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'parent']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'category', 'base_price', 'product_type', 'is_available', 'is_featured', 'created_at']
    list_filter = ['is_available', 'is_featured', 'product_type', 'category']
    search_fields = ['name', 'description', 'shop__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock_quantity', 'effective_price', 'is_active']
    list_filter = ['size', 'is_active']
    search_fields = ['product__name', 'sku', 'color']
