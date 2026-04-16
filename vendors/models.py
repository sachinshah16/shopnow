from django.db import models
from django.conf import settings


class Vendor(models.Model):
    """Vendor profile linked to a User with role='vendor'."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=200)
    gstin = models.CharField(max_length=20, blank=True, verbose_name='GSTIN')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name

    class Meta:
        ordering = ['-created_at']


class Shop(models.Model):
    """A physical shop belonging to a vendor."""

    SHOP_TYPE_CHOICES = (
        ('budget', 'Budget Friendly'),
        ('premium', 'Premium'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    shop_type = models.CharField(max_length=10, choices=SHOP_TYPE_CHOICES, default='budget')
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='shops/banners/', blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.count()

    class Meta:
        ordering = ['-created_at']
