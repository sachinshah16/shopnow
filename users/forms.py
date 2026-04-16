from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomerRegistrationForm(UserCreationForm):
    """Registration form for customers."""

    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user


class VendorRegistrationForm(UserCreationForm):
    """Registration form for vendors."""

    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    business_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Business Name'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'vendor'
        if commit:
            user.save()
            from vendors.models import Vendor
            Vendor.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name']
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'pincode', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your address'}),
        }
