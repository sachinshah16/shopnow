from django import forms
from .models import Shop


class ShopForm(forms.ModelForm):
    """Form for creating/editing a shop."""

    class Meta:
        model = Shop
        fields = ['name', 'description', 'shop_type', 'address', 'city', 'pincode',
                  'latitude', 'longitude', 'logo', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Shop Name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your shop...'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Shop Address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'Pincode'}),
            'latitude': forms.NumberInput(attrs={'placeholder': 'Latitude (optional)', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'placeholder': 'Longitude (optional)', 'step': 'any'}),
        }
