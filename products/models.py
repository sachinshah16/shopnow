from django.db import models
from django.utils.text import slugify
import uuid


class Category(models.Model):
    """Product category with optional parent for subcategories."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Product(models.Model):
    """A product listed by a shop."""

    TYPE_CHOICES = (
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('ethnic', 'Ethnic'),
        ('sports', 'Sports'),
        ('party', 'Party Wear'),
    )

    shop = models.ForeignKey('vendors.Shop', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='casual')
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def price_display(self):
        return f"₹ {self.base_price:,.0f}"

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants.filter(is_active=True))

    @property
    def in_stock(self):
        return self.total_stock > 0

    class Meta:
        ordering = ['-created_at']


class ProductImage(models.Model):
    """Multiple images per product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        ordering = ['-is_primary', 'created_at']


class ProductVariant(models.Model):
    """Specific variant of a product (size + color + type combination)."""

    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('FREE', 'Free Size'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7, default='#000000', help_text='Hex color code for display')
    variant_type = models.CharField(max_length=20, choices=Product.TYPE_CHOICES, default='casual')
    sku = models.CharField(max_length=50, unique=True, blank=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         help_text='Leave blank to use product base price')
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.size}/{self.color}"

    @property
    def effective_price(self):
        return self.price_override if self.price_override else self.product.base_price

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{self.product.id or 0}-{self.size}-{self.color[:3].upper()}-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['size', 'color']
        unique_together = ['product', 'size', 'color', 'variant_type']
