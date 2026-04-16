from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from .models import Vendor, Shop
from .forms import ShopForm
from products.models import Product, ProductImage, ProductVariant
from products.forms import ProductForm, ProductVariantForm, ProductImageForm
from orders.models import Order, OrderItem


class VendorRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be a vendor."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_vendor:
            messages.error(request, 'You need a vendor account to access this page.')
            return redirect('products:home')
        return super().dispatch(request, *args, **kwargs)


class VendorDashboardView(VendorRequiredMixin, View):
    """Main vendor dashboard with stats."""

    def get(self, request):
        vendor = request.user.vendor_profile
        shops = vendor.shops.all()
        total_products = Product.objects.filter(shop__vendor=vendor).count()
        recent_orders = Order.objects.filter(
            items__variant__product__shop__vendor=vendor
        ).distinct().order_by('-created_at')[:10]
        pending_orders = Order.objects.filter(
            items__variant__product__shop__vendor=vendor,
            status='pending'
        ).distinct().count()

        context = {
            'vendor': vendor,
            'shops': shops,
            'total_products': total_products,
            'recent_orders': recent_orders,
            'pending_orders': pending_orders,
        }
        return render(request, 'vendors/dashboard.html', context)


class ShopCreateView(VendorRequiredMixin, View):
    """Create a new shop."""

    def get(self, request):
        form = ShopForm()
        return render(request, 'vendors/shop_form.html', {'form': form, 'action': 'Create'})

    def post(self, request):
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.vendor = request.user.vendor_profile
            shop.save()
            messages.success(request, f'Shop "{shop.name}" created successfully!')
            return redirect('vendors:dashboard')
        return render(request, 'vendors/shop_form.html', {'form': form, 'action': 'Create'})


class ShopUpdateView(VendorRequiredMixin, View):
    """Edit an existing shop."""

    def get(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk, vendor=request.user.vendor_profile)
        form = ShopForm(instance=shop)
        return render(request, 'vendors/shop_form.html', {'form': form, 'action': 'Update', 'shop': shop})

    def post(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk, vendor=request.user.vendor_profile)
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop updated successfully!')
            return redirect('vendors:dashboard')
        return render(request, 'vendors/shop_form.html', {'form': form, 'action': 'Update', 'shop': shop})


class VendorProductListView(VendorRequiredMixin, View):
    """List vendor's products for management."""

    def get(self, request):
        vendor = request.user.vendor_profile
        products = Product.objects.filter(shop__vendor=vendor).select_related('shop', 'category')
        return render(request, 'vendors/product_list.html', {'products': products})


class VendorProductCreateView(VendorRequiredMixin, View):
    """Create a new product."""

    def get(self, request):
        vendor = request.user.vendor_profile
        shops = vendor.shops.filter(is_active=True)
        form = ProductForm()
        form.fields['shop'].queryset = shops
        variant_form = ProductVariantForm()
        image_form = ProductImageForm()
        return render(request, 'vendors/product_form.html', {
            'form': form, 'variant_form': variant_form, 'image_form': image_form, 'action': 'Add'
        })

    def post(self, request):
        vendor = request.user.vendor_profile
        shops = vendor.shops.filter(is_active=True)
        form = ProductForm(request.POST)
        form.fields['shop'].queryset = shops

        if form.is_valid():
            product = form.save()

            # Handle images
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                ProductImage.objects.create(product=product, image=img, is_primary=(i == 0))

            # Handle variants
            sizes = request.POST.getlist('variant_size')
            colors = request.POST.getlist('variant_color')
            color_codes = request.POST.getlist('variant_color_code')
            stocks = request.POST.getlist('variant_stock')
            prices = request.POST.getlist('variant_price')

            for j in range(len(sizes)):
                if sizes[j]:
                    ProductVariant.objects.create(
                        product=product,
                        size=sizes[j],
                        color=colors[j] if j < len(colors) else 'Default',
                        color_code=color_codes[j] if j < len(color_codes) else '#000000',
                        stock_quantity=int(stocks[j]) if j < len(stocks) and stocks[j] else 0,
                        price_override=float(prices[j]) if j < len(prices) and prices[j] else None,
                        variant_type=product.product_type,
                    )

            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('vendors:products')

        variant_form = ProductVariantForm()
        image_form = ProductImageForm()
        return render(request, 'vendors/product_form.html', {
            'form': form, 'variant_form': variant_form, 'image_form': image_form, 'action': 'Add'
        })


class VendorProductEditView(VendorRequiredMixin, View):
    """Edit a product."""

    def get(self, request, pk):
        vendor = request.user.vendor_profile
        product = get_object_or_404(Product, pk=pk, shop__vendor=vendor)
        form = ProductForm(instance=product)
        form.fields['shop'].queryset = vendor.shops.filter(is_active=True)
        variants = product.variants.all()
        images = product.images.all()
        return render(request, 'vendors/product_form.html', {
            'form': form, 'action': 'Edit', 'product': product,
            'existing_variants': variants, 'existing_images': images,
            'variant_form': ProductVariantForm(), 'image_form': ProductImageForm(),
        })

    def post(self, request, pk):
        vendor = request.user.vendor_profile
        product = get_object_or_404(Product, pk=pk, shop__vendor=vendor)
        form = ProductForm(request.POST, instance=product)
        form.fields['shop'].queryset = vendor.shops.filter(is_active=True)

        if form.is_valid():
            product = form.save()

            # Handle new images
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)

            # Handle new variants
            sizes = request.POST.getlist('variant_size')
            colors = request.POST.getlist('variant_color')
            color_codes = request.POST.getlist('variant_color_code')
            stocks = request.POST.getlist('variant_stock')
            prices = request.POST.getlist('variant_price')

            for j in range(len(sizes)):
                if sizes[j]:
                    ProductVariant.objects.create(
                        product=product,
                        size=sizes[j],
                        color=colors[j] if j < len(colors) else 'Default',
                        color_code=color_codes[j] if j < len(color_codes) else '#000000',
                        stock_quantity=int(stocks[j]) if j < len(stocks) and stocks[j] else 0,
                        price_override=float(prices[j]) if j < len(prices) and prices[j] else None,
                        variant_type=product.product_type,
                    )

            messages.success(request, 'Product updated successfully!')
            return redirect('vendors:products')

        return render(request, 'vendors/product_form.html', {
            'form': form, 'action': 'Edit', 'product': product,
            'variant_form': ProductVariantForm(), 'image_form': ProductImageForm(),
        })


class VendorProductDeleteView(VendorRequiredMixin, View):
    """Delete a product."""

    def post(self, request, pk):
        vendor = request.user.vendor_profile
        product = get_object_or_404(Product, pk=pk, shop__vendor=vendor)
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('vendors:products')


class VendorOrderListView(VendorRequiredMixin, View):
    """List orders for vendor's shops."""

    def get(self, request):
        vendor = request.user.vendor_profile
        orders = Order.objects.filter(
            items__variant__product__shop__vendor=vendor
        ).distinct().order_by('-created_at')
        return render(request, 'vendors/order_list.html', {'orders': orders})


class VendorOrderDetailView(VendorRequiredMixin, View):
    """View and update an order."""

    def get(self, request, pk):
        vendor = request.user.vendor_profile
        order = get_object_or_404(Order, pk=pk)
        # Only show items from this vendor's shops
        items = order.items.filter(variant__product__shop__vendor=vendor)
        return render(request, 'vendors/order_detail.html', {'order': order, 'items': items})

    def post(self, request, pk):
        vendor = request.user.vendor_profile
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            is_valid, error = order.clean_transition(request.user, new_status)
            if is_valid:
                order.status = new_status
                order.save()
                messages.success(request, f'Order {order.order_number} status updated to {order.get_status_display()}.')
            else:
                messages.error(request, error)
        return redirect('vendors:order_detail', pk=pk)


class VendorVariantDeleteView(VendorRequiredMixin, View):
    """Delete a product variant."""

    def post(self, request, pk):
        variant = get_object_or_404(ProductVariant, pk=pk, product__shop__vendor=request.user.vendor_profile)
        variant.delete()
        return JsonResponse({'status': 'ok'})


class VendorImageDeleteView(VendorRequiredMixin, View):
    """Delete a product image."""

    def post(self, request, pk):
        image = get_object_or_404(ProductImage, pk=pk, product__shop__vendor=request.user.vendor_profile)
        image.delete()
        return JsonResponse({'status': 'ok'})


class VendorQuickSellAPIView(VendorRequiredMixin, View):
    """Vendor feature to quickly look up and sell an item offline via AJAX."""

    def get(self, request):
        product_code = request.GET.get('product_code', '').strip()
        vendor = request.user.vendor_profile

        if not product_code:
            return JsonResponse({'status': 'error', 'message': 'Please enter a product code.'}, status=400)

        # Lookup by SKU or ID
        variant = None
        try:
            variant = ProductVariant.objects.get(sku=product_code, product__shop__vendor=vendor)
        except ProductVariant.DoesNotExist:
            if product_code.isdigit():
                try:
                    variant = ProductVariant.objects.get(id=int(product_code), product__shop__vendor=vendor)
                except ProductVariant.DoesNotExist:
                    pass
        
        if not variant:
            return JsonResponse({'status': 'error', 'message': 'Product code not found in your inventory.'}, status=404)
            
        product = variant.product
        return JsonResponse({
            'status': 'success',
            'product': {
                'id': variant.id,
                'name': product.name,
                'sku': variant.sku,
                'variant_info': f"{variant.size} / {variant.color}",
                'price': float(variant.effective_price),
                'stock': variant.stock_quantity,
                'image_url': product.primary_image.image.url if product.primary_image else None
            }
        })

    def post(self, request):
        variant_id = request.POST.get('variant_id')
        vendor = request.user.vendor_profile

        if not variant_id:
            return JsonResponse({'status': 'error', 'message': 'Invalid product selection.'}, status=400)

        try:
            variant = ProductVariant.objects.get(id=variant_id, product__shop__vendor=vendor)
            if variant.stock_quantity > 0:
                variant.stock_quantity -= 1
                if variant.stock_quantity == 0:
                    variant.is_active = False
                variant.save()

                product = variant.product
                if not product.variants.filter(is_active=True, stock_quantity__gt=0).exists():
                    product.is_available = False
                    product.save()

                return JsonResponse({
                    'status': 'success', 
                    'message': f'Sold! {product.name} ({variant.size}/{variant.color}) stock reduced to {variant.stock_quantity}.'
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Item is already out of stock!'}, status=400)

        except ProductVariant.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Variant not found.'}, status=404)
