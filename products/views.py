from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator
from .models import Category, Product, ProductVariant
from vendors.models import Shop
import math
import json
import urllib.request
import urllib.parse


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS coordinates."""
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class SplashView(View):
    """Splash/landing page."""

    def get(self, request):
        return render(request, 'splash.html')


class ReverseGeocodeView(View):
    """AJAX endpoint: Convert lat/lng to a readable location name."""

    def get(self, request):
        lat = request.GET.get('lat', '')
        lng = request.GET.get('lng', '')
        if not lat or not lng:
            return JsonResponse({'location': 'Unknown'})

        try:
            url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=16&addressdetails=1'
            req = urllib.request.Request(url, headers={'User-Agent': 'ShopNow/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                addr = data.get('address', {})
                area = addr.get('suburb') or addr.get('neighbourhood') or addr.get('road', '')
                city = addr.get('city') or addr.get('town') or addr.get('state_district', '')
                location = f"{area}, {city}" if area and city else city or area or 'Unknown'
                return JsonResponse({'location': location})
        except Exception:
            return JsonResponse({'location': 'Your Location'})


class GeoSearchView(View):
    """AJAX endpoint: Search for locations by name/pincode via Nominatim proxy."""

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return JsonResponse({'results': []})

        try:
            url = (
                f'https://nominatim.openstreetmap.org/search'
                f'?q={urllib.parse.quote(query)}'
                f'&format=json&addressdetails=1&limit=6&countrycodes=in'
            )
            req = urllib.request.Request(url, headers={'User-Agent': 'ShopNow/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = json.loads(resp.read())
                results = []
                for item in raw:
                    addr = item.get('address', {})
                    area = (addr.get('suburb') or addr.get('neighbourhood')
                            or addr.get('road') or addr.get('city_district') or '')
                    city = (addr.get('city') or addr.get('town')
                            or addr.get('state_district') or addr.get('state') or '')
                    name = area or item.get('display_name', '').split(',')[0]
                    short_addr = ', '.join(item.get('display_name', '').split(',')[:3])
                    results.append({
                        'lat': item['lat'],
                        'lng': item['lon'],
                        'name': name,
                        'city': city,
                        'display': f"{name}, {city}" if name and city else name or city,
                        'address': short_addr,
                    })
                return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'results': [], 'error': str(e)})


class HomeView(View):
    """Home page with shop/item toggle, search, and filters."""

    def get(self, request):
        mode = request.GET.get('mode', 'shops')
        search_query = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')
        shop_type = request.GET.get('shop_type', '')
        price_min = request.GET.get('price_min', '')
        price_max = request.GET.get('price_max', '')

        # User location from query params (set by JS geolocation)
        user_lat = request.GET.get('lat', '')
        user_lng = request.GET.get('lng', '')

        categories = Category.objects.filter(is_active=True, parent=None)

        if mode == 'items':
            # Product browsing mode
            products = Product.objects.filter(is_available=True).select_related('shop', 'category')

            if search_query:
                products = products.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(shop__name__icontains=search_query)
                )

            if category_slug:
                products = products.filter(category__slug=category_slug)

            if price_min:
                products = products.filter(base_price__gte=price_min)
            if price_max:
                products = products.filter(base_price__lte=price_max)

            # Attach shop distance to each product
            if user_lat and user_lng:
                try:
                    ulat, ulng = float(user_lat), float(user_lng)
                    for p in products:
                        if p.shop.latitude and p.shop.longitude:
                            p.shop.distance_km = round(haversine(ulat, ulng, p.shop.latitude, p.shop.longitude), 1)
                        else:
                            p.shop.distance_km = None
                except (ValueError, TypeError):
                    pass

            paginator = Paginator(products, 12)
            page = request.GET.get('page', 1)
            products = paginator.get_page(page)

            context = {
                'mode': 'items',
                'products': products,
                'categories': categories,
                'search_query': search_query,
                'category_slug': category_slug,
            }
        else:
            # Shop browsing mode
            shops = Shop.objects.filter(is_active=True)

            if search_query:
                shops = shops.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

            if shop_type:
                shops = shops.filter(shop_type=shop_type)

            # Calculate distances and sort by proximity
            budget_shops = list(shops.filter(shop_type='budget'))
            premium_shops = list(shops.filter(shop_type='premium'))

            if user_lat and user_lng:
                try:
                    ulat, ulng = float(user_lat), float(user_lng)
                    for shop in budget_shops + premium_shops:
                        if shop.latitude and shop.longitude:
                            shop.distance_km = round(haversine(ulat, ulng, shop.latitude, shop.longitude), 1)
                        else:
                            shop.distance_km = None
                    budget_shops.sort(key=lambda s: s.distance_km if s.distance_km is not None else 999)
                    premium_shops.sort(key=lambda s: s.distance_km if s.distance_km is not None else 999)
                except (ValueError, TypeError):
                    pass

            context = {
                'mode': 'shops',
                'budget_shops': budget_shops,
                'premium_shops': premium_shops,
                'all_shops': shops,
                'categories': categories,
                'search_query': search_query,
                'shop_type': shop_type,
            }

        return render(request, 'products/home.html', context)



class ShopListView(View):
    """Browse all shops."""

    def get(self, request):
        shops = Shop.objects.filter(is_active=True)
        search_query = request.GET.get('q', '')
        shop_type = request.GET.get('type', '')

        if search_query:
            shops = shops.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        if shop_type:
            shops = shops.filter(shop_type=shop_type)

        paginator = Paginator(shops, 12)
        page = request.GET.get('page', 1)
        shops = paginator.get_page(page)

        return render(request, 'products/shop_list.html', {
            'shops': shops, 'search_query': search_query, 'shop_type': shop_type
        })


class ShopDetailView(View):
    """View a single shop and its products."""

    def get(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk, is_active=True)
        products = shop.products.filter(is_available=True)
        category_slug = request.GET.get('category', '')

        if category_slug:
            products = products.filter(category__slug=category_slug)

        categories = Category.objects.filter(
            products__shop=shop, is_active=True
        ).distinct()

        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)

        return render(request, 'products/shop_detail.html', {
            'shop': shop, 'products': products, 'categories': categories,
            'category_slug': category_slug,
        })


class ProductListView(View):
    """Browse all products with filters."""

    def get(self, request):
        products = Product.objects.filter(is_available=True).select_related('shop', 'category')
        categories = Category.objects.filter(is_active=True, parent=None)

        search_query = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')
        product_type = request.GET.get('type', '')
        price_min = request.GET.get('price_min', '')
        price_max = request.GET.get('price_max', '')
        sort_by = request.GET.get('sort', '-created_at')

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        if category_slug:
            products = products.filter(category__slug=category_slug)

        if product_type:
            products = products.filter(product_type=product_type)

        if price_min:
            products = products.filter(base_price__gte=price_min)
        if price_max:
            products = products.filter(base_price__lte=price_max)

        if sort_by in ['base_price', '-base_price', 'name', '-name', '-created_at']:
            products = products.order_by(sort_by)

        price_range = Product.objects.filter(is_available=True).aggregate(
            min_price=Min('base_price'), max_price=Max('base_price')
        )

        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)

        return render(request, 'products/product_list.html', {
            'products': products, 'categories': categories,
            'search_query': search_query, 'category_slug': category_slug,
            'product_type': product_type, 'price_min': price_min,
            'price_max': price_max, 'sort_by': sort_by, 'price_range': price_range,
        })


class ProductDetailView(View):
    """Product detail page with variant selection."""

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_available=True)
        variants = product.variants.filter(is_active=True)
        images = product.images.all()
        related_products = Product.objects.filter(
            category=product.category, is_available=True
        ).exclude(pk=product.pk)[:4]

        # Get unique sizes and colors for the variant selector
        size_list = list(dict.fromkeys(variants.values_list('size', flat=True)))
        color_seen = {}
        for v in variants:
            if v.color not in color_seen:
                color_seen[v.color] = v.color_code
        color_list = [{'color': c, 'color_code': code} for c, code in color_seen.items()]

        return render(request, 'products/product_detail.html', {
            'product': product, 'variants': variants, 'images': images,
            'related_products': related_products, 'sizes': size_list, 'colors': color_list,
        })


class GetVariantView(View):
    """AJAX endpoint to get variant info by size + color."""

    def get(self, request):
        product_id = request.GET.get('product_id')
        size = request.GET.get('size')
        color = request.GET.get('color')

        try:
            variant = ProductVariant.objects.get(
                product_id=product_id, size=size, color=color, is_active=True
            )
            return JsonResponse({
                'found': True,
                'variant_id': variant.id,
                'price': str(variant.effective_price),
                'stock': variant.stock_quantity,
                'in_stock': variant.in_stock,
                'sku': variant.sku,
            })
        except ProductVariant.DoesNotExist:
            return JsonResponse({'found': False})


class SearchView(View):
    """Combined search for shops and products."""

    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return render(request, 'products/search_results.html', {'query': ''})

        shops = Shop.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:6]

        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        ).select_related('shop', 'category')

        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)

        return render(request, 'products/search_results.html', {
            'query': query, 'shops': shops, 'products': products,
        })


class SearchSuggestView(View):
    """AJAX search suggestions."""

    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})

        products = Product.objects.filter(
            name__icontains=query, is_available=True
        ).values('name', 'slug', 'base_price')[:5]

        shops = Shop.objects.filter(
            name__icontains=query, is_active=True
        ).values('name', 'id')[:3]

        results = []
        for p in products:
            results.append({'type': 'product', 'name': p['name'], 'slug': p['slug'], 'price': str(p['base_price'])})
        for s in shops:
            results.append({'type': 'shop', 'name': s['name'], 'id': s['id']})

        return JsonResponse({'results': results})
