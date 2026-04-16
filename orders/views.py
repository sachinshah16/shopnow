from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Cart, CartItem, Order, OrderItem


class CartView(LoginRequiredMixin, View):
    """View shopping cart."""

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('variant__product').all()
        return render(request, 'orders/cart.html', {'cart': cart, 'items': items})


class AddToCartView(LoginRequiredMixin, View):
    """Add a product variant to cart (AJAX)."""

    def post(self, request):
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        if not variant_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Please select a size and color'}, status=400)
            messages.error(request, 'Please select a size and color.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        from products.models import ProductVariant
        try:
            variant = ProductVariant.objects.get(pk=variant_id, is_active=True)
        except ProductVariant.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Variant not found'}, status=404)
            messages.error(request, 'Product variant not found.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if quantity > variant.stock_quantity:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': f'Only {variant.stock_quantity} items in stock'}, status=400)
            messages.error(request, f'Only {variant.stock_quantity} items available in stock.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'message': f'{variant.product.name} added to cart!',
                'cart_count': cart.total_items,
            })

        messages.success(request, f'{variant.product.name} added to cart!')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class UpdateCartView(LoginRequiredMixin, View):
    """Update cart item quantity (AJAX)."""

    def post(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.variant.stock_quantity:
                quantity = cart_item.variant.stock_quantity
            cart_item.quantity = quantity
            cart_item.save()

        cart = cart_item.cart if quantity > 0 else Cart.objects.get(user=request.user)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'cart_count': cart.total_items,
                'cart_total': str(cart.total_amount),
                'item_subtotal': str(cart_item.subtotal) if quantity > 0 else '0',
            })

        return redirect('orders:cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove item from cart."""

    def post(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart_item.delete()

        cart = Cart.objects.get(user=request.user)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'cart_count': cart.total_items,
                'cart_total': str(cart.total_amount),
            })

        messages.info(request, 'Item removed from cart.')
        return redirect('orders:cart')


class CheckoutView(LoginRequiredMixin, View):
    """Checkout page — enter address and place order."""

    def get(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.select_related('variant__product').all()
        if not items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('orders:cart')
        return render(request, 'orders/checkout.html', {'cart': cart, 'items': items})

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.select_related('variant__product').all()

        if not items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('orders:cart')

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_amount,
            delivery_address=request.POST.get('delivery_address', ''),
            delivery_city=request.POST.get('delivery_city', ''),
            delivery_state=request.POST.get('delivery_state', ''),
            delivery_pincode=request.POST.get('delivery_pincode', ''),
            phone=request.POST.get('phone', ''),
            notes=request.POST.get('notes', ''),
        )

        # Create order items and deduct stock
        for item in items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_name=item.variant.product.name,
                variant_info=f"{item.variant.size} / {item.variant.color}",
                quantity=item.quantity,
                price=item.variant.effective_price,
            )
            # Deduct stock
            item.variant.stock_quantity = max(0, item.variant.stock_quantity - item.quantity)
            if item.variant.stock_quantity == 0:
                item.variant.is_active = False
            item.variant.save()

            product = item.variant.product
            if not product.variants.filter(is_active=True, stock_quantity__gt=0).exists():
                product.is_available = False
                product.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f'Order {order.order_number} placed successfully! Delivery within 12 hours.')
        return redirect('orders:order_success', pk=order.pk)


class OrderSuccessView(LoginRequiredMixin, View):
    """Order confirmation page."""

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        return render(request, 'orders/order_success.html', {'order': order})


class OrderListView(LoginRequiredMixin, View):
    """List customer's orders."""

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return render(request, 'orders/order_list.html', {'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    """View order details."""

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        items = order.items.all()
        return render(request, 'orders/order_detail.html', {'order': order, 'items': items})


class CustomerCancelOrderView(LoginRequiredMixin, View):
    """Customer action to cancel an order."""
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        is_valid, error = order.clean_transition(request.user, 'cancelled')
        if is_valid:
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order {order.order_number} has been cancelled successfully.')
        else:
            messages.error(request, error)
        return redirect('orders:order_detail', pk=pk)


class QuickAddToCartView(LoginRequiredMixin, View):
    """Quick add to cart from product listing (uses first available variant)."""

    def post(self, request):
        product_id = request.POST.get('product_id')
        from products.models import Product
        try:
            product = Product.objects.get(pk=product_id, is_available=True)
            variant = product.variants.filter(is_active=True, stock_quantity__gt=0).first()
            if not variant:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Product is out of stock'}, status=400)
                messages.error(request, 'Product is out of stock.')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
            if not created:
                cart_item.quantity += 1
            cart_item.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'message': f'{product.name} added to cart!',
                    'cart_count': cart.total_items,
                })

            messages.success(request, f'{product.name} added to cart!')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        except Product.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Product not found'}, status=404)
            messages.error(request, 'Product not found.')
            return redirect(request.META.get('HTTP_REFERER', '/'))


class PincodeLookupView(View):
    """API to lookup city, state, district from Indian pincode."""

    def get(self, request):
        pincode = request.GET.get('pincode', '').strip()
        if not pincode or len(pincode) != 6 or not pincode.isdigit():
            return JsonResponse({'error': 'Please enter a valid 6-digit pincode'}, status=400)

        import urllib.request
        import json

        try:
            api_url = f'https://api.postalpincode.in/pincode/{pincode}'
            req = urllib.request.Request(api_url, headers={'User-Agent': 'ShopNow/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

            if data and data[0].get('Status') == 'Success' and data[0].get('PostOffice'):
                post_offices = data[0]['PostOffice']
                first = post_offices[0]

                # Collect all unique area names for suggestions
                areas = [po['Name'] for po in post_offices]

                return JsonResponse({
                    'status': 'success',
                    'city': first.get('District', ''),
                    'state': first.get('State', ''),
                    'district': first.get('District', ''),
                    'country': first.get('Country', 'India'),
                    'areas': areas,
                })
            else:
                return JsonResponse({'error': 'Invalid pincode or no data found'}, status=404)

        except Exception:
            return JsonResponse({'error': 'Could not fetch pincode details. Please enter manually.'}, status=500)

