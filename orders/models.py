from django.db import models
from django.conf import settings
import uuid
from datetime import timedelta
from django.utils import timezone


class Cart(models.Model):
    """Shopping cart for a user."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Individual item in a cart, linked to a product variant."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    @property
    def subtotal(self):
        return self.variant.effective_price * self.quantity

    class Meta:
        unique_together = ['cart', 'variant']


class Order(models.Model):
    """Customer order."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=30, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100, blank=True)
    delivery_pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = timezone.now().strftime('%Y%m%d')
            unique = uuid.uuid4().hex[:6].upper()
            self.order_number = f"SN-{date_str}-{unique}"
        super().save(*args, **kwargs)

    @property
    def status_display_class(self):
        """Bootstrap class for status badge."""
        mapping = {
            'pending': 'warning',
            'confirmed': 'info',
            'packed': 'primary',
            'out_for_delivery': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return mapping.get(self.status, 'secondary')

    def clean_transition(self, user, new_status):
        """Enforces safe strict status transitions based on the user's role."""
        if self.status == new_status:
            return True, ""

        if user.is_superuser or user.role == 'admin':
            if new_status == 'cancelled' and self.status == 'delivered':
                return False, "Cannot cancel a delivered order."
            if new_status in ['out_for_delivery', 'delivered', 'cancelled']:
                return True, ""
            return False, "Admin should only process delivery or cancellations."

        if user.role == 'vendor':
            if new_status == 'cancelled':
                if self.status == 'pending':
                    return True, ""
                return False, "You can only cancel an order before it is confirmed."
            if new_status in ['confirmed', 'packed']:
                if self.status in ['pending', 'confirmed']:
                    return True, ""
                return False, f"Cannot revert status to {new_status}."
            return False, f"Vendors cannot update status to {new_status}."

        if user.role == 'delivery':
            if new_status == 'cancelled':
                if self.status == 'out_for_delivery':
                    return True, ""
                return False, "Delivery agent can only cancel after picking up for delivery."
            if new_status == 'delivered':
                if self.status == 'out_for_delivery':
                    return True, ""
                return False, "Order must be out for delivery first."
            return False, "Unauthorized transition for delivery agent."

        if getattr(user, 'is_customer', True):
            if new_status == 'cancelled':
                if self.status not in ['delivered', 'cancelled']:
                    return True, ""
                return False, "You cannot cancel an order that has already been delivered."
            return False, "Customers can only cancel orders."

        return False, "Action unauthorized."

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Individual item in an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    variant_info = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Delivery(models.Model):
    """Delivery tracking for an order."""

    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    assigned_to = models.CharField(max_length=200, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery for {self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.estimated_delivery and self.assigned_at:
            self.estimated_delivery = self.assigned_at + timedelta(hours=12)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Deliveries'
