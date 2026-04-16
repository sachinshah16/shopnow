from django import forms
from .models import Product, ProductVariant, ProductImage


class ProductForm(forms.ModelForm):
    """Form for creating/editing a product."""

    class Meta:
        model = Product
        fields = ['shop', 'category', 'name', 'description', 'base_price', 'product_type',
                  'is_available', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Product Description'}),
            'base_price': forms.NumberInput(attrs={'placeholder': '₹ Price', 'step': '0.01'}),
        }


class ProductVariantForm(forms.ModelForm):
    """Form for adding product variants."""

    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'color_code', 'stock_quantity', 'price_override']
        widgets = {
            'color': forms.TextInput(attrs={'placeholder': 'e.g., Red'}),
            'color_code': forms.TextInput(attrs={'type': 'color', 'value': '#000000'}),
            'stock_quantity': forms.NumberInput(attrs={'placeholder': 'Stock', 'min': 0}),
            'price_override': forms.NumberInput(attrs={'placeholder': '₹ Override (optional)', 'step': '0.01'}),
        }


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images."""

    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']
