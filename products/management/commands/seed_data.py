from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from vendors.models import Vendor, Shop
from products.models import Category, Product, ProductVariant, ProductImage
from orders.models import Cart

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data for ShopNow'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding ShopNow database...\n')

        # ---- Create Admin ----
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@shopnow.in',
                'first_name': 'Admin',
                'last_name': 'ShopNow',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✅ Admin user created (admin/admin123)'))

        # ---- Create Customers ----
        customer1, created = User.objects.get_or_create(
            username='ravi',
            defaults={
                'email': 'ravi@example.com',
                'first_name': 'Ravi',
                'last_name': 'Kumar',
                'role': 'customer',
                'phone': '9876543210',
                'city': 'Bangalore',
                'pincode': '560076',
                'address': '123, BTM Layout, 2nd Stage',
            }
        )
        if created:
            customer1.set_password('customer123')
            customer1.save()
            Cart.objects.get_or_create(user=customer1)
            self.stdout.write(self.style.SUCCESS('✅ Customer Ravi created (ravi/customer123)'))

        customer2, created = User.objects.get_or_create(
            username='priya',
            defaults={
                'email': 'priya@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'role': 'customer',
                'phone': '9876543211',
                'city': 'Bangalore',
                'pincode': '560078',
                'address': '45, Koramangala, 4th Block',
            }
        )
        if created:
            customer2.set_password('customer123')
            customer2.save()
            Cart.objects.get_or_create(user=customer2)
            self.stdout.write(self.style.SUCCESS('✅ Customer Priya created (priya/customer123)'))

        # ---- Create Vendors ----
        vendor_user1, created = User.objects.get_or_create(
            username='vendor1',
            defaults={
                'email': 'vendor1@example.com',
                'first_name': 'Amit',
                'last_name': 'Patel',
                'role': 'vendor',
                'phone': '9876543220',
                'city': 'Bangalore',
            }
        )
        if created:
            vendor_user1.set_password('vendor123')
            vendor_user1.save()
        vendor1, _ = Vendor.objects.get_or_create(
            user=vendor_user1,
            defaults={'business_name': 'Trendy Collections', 'is_verified': True}
        )

        vendor_user2, created = User.objects.get_or_create(
            username='vendor2',
            defaults={
                'email': 'vendor2@example.com',
                'first_name': 'Sneha',
                'last_name': 'Reddy',
                'role': 'vendor',
                'phone': '9876543230',
                'city': 'Bangalore',
            }
        )
        if created:
            vendor_user2.set_password('vendor123')
            vendor_user2.save()
        vendor2, _ = Vendor.objects.get_or_create(
            user=vendor_user2,
            defaults={'business_name': 'Elite Boutique', 'is_verified': True}
        )
        self.stdout.write(self.style.SUCCESS('✅ Vendors created (vendor1/vendor123, vendor2/vendor123)'))

        # ---- Create Shops ----
        shop1, _ = Shop.objects.get_or_create(
            vendor=vendor1, name='Trendy Collections',
            defaults={
                'description': 'Your one-stop destination for trendy casual and formal wear at affordable prices.',
                'shop_type': 'budget',
                'address': '12, Commercial Street',
                'city': 'Bangalore',
                'pincode': '560001',
                'rating': 4.2,
            }
        )

        shop2, _ = Shop.objects.get_or_create(
            vendor=vendor1, name='Fashion Hub',
            defaults={
                'description': 'Latest fashion trends for men, women and kids.',
                'shop_type': 'budget',
                'address': '56, MG Road',
                'city': 'Bangalore',
                'pincode': '560002',
                'rating': 4.0,
            }
        )

        shop3, _ = Shop.objects.get_or_create(
            vendor=vendor2, name='Elite Boutique',
            defaults={
                'description': 'Premium designer wear and exclusive collections for the fashion-forward.',
                'shop_type': 'premium',
                'address': '78, Indiranagar, 100ft Road',
                'city': 'Bangalore',
                'pincode': '560038',
                'rating': 4.7,
            }
        )

        shop4, _ = Shop.objects.get_or_create(
            vendor=vendor2, name='Style Emporium',
            defaults={
                'description': 'Curated premium fashion from top designers.',
                'shop_type': 'premium',
                'address': '23, UB City Mall',
                'city': 'Bangalore',
                'pincode': '560001',
                'rating': 4.5,
            }
        )
        self.stdout.write(self.style.SUCCESS('✅ 4 Shops created'))

        # ---- Create Categories ----
        categories_data = [
            ('Men', 'men'),
            ('Women', 'women'),
            ('Kids', 'kids'),
            ('Accessories', 'accessories'),
            ('Footwear', 'footwear'),
            ('Ethnic Wear', 'ethnic-wear'),
        ]
        categories = {}
        for name, slug in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, slug=slug)
            categories[slug] = cat
        self.stdout.write(self.style.SUCCESS('✅ 6 Categories created'))

        # ---- Create Products ----
        products_data = [
            # Shop 1 — Trendy Collections
            {'shop': shop1, 'cat': 'women', 'name': 'Floral Dress', 'price': 899, 'type': 'casual',
             'desc': 'Beautiful floral print summer dress with comfortable fit.'},
            {'shop': shop1, 'cat': 'men', 'name': 'Casual Shirt', 'price': 599, 'type': 'casual',
             'desc': 'Cotton casual shirt perfect for everyday wear.'},
            {'shop': shop1, 'cat': 'women', 'name': 'Designer Saree', 'price': 1499, 'type': 'ethnic',
             'desc': 'Elegant designer saree with rich silk blend.'},
            {'shop': shop1, 'cat': 'accessories', 'name': 'Leather Handbag', 'price': 1200, 'type': 'formal',
             'desc': 'Premium quality leather handbag for daily use.'},

            # Shop 2 — Fashion Hub
            {'shop': shop2, 'cat': 'men', 'name': 'Denim Jacket', 'price': 1800, 'type': 'casual',
             'desc': 'Classic denim jacket with modern fit.'},
            {'shop': shop2, 'cat': 'women', 'name': 'Denim Jacket', 'price': 1800, 'type': 'casual',
             'desc': 'Stylish women\'s denim jacket.'},
            {'shop': shop2, 'cat': 'kids', 'name': 'Kids T-Shirt Pack', 'price': 499, 'type': 'casual',
             'desc': 'Colorful printed cotton t-shirts for kids (pack of 3).'},
            {'shop': shop2, 'cat': 'men', 'name': 'Formal Trousers', 'price': 1299, 'type': 'formal',
             'desc': 'Slim fit formal trousers in premium fabric.'},

            # Shop 3 — Elite Boutique
            {'shop': shop3, 'cat': 'women', 'name': 'Silk Saree', 'price': 3500, 'type': 'ethnic',
             'desc': 'Handwoven pure silk saree with zari work.'},
            {'shop': shop3, 'cat': 'men', 'name': 'Premium Blazer', 'price': 4500, 'type': 'formal',
             'desc': 'Italian-cut premium wool blend blazer.'},
            {'shop': shop3, 'cat': 'women', 'name': 'Evening Gown', 'price': 5500, 'type': 'party',
             'desc': 'Stunning floor-length evening gown for special occasions.'},
            {'shop': shop3, 'cat': 'accessories', 'name': 'Designer Watch', 'price': 2800, 'type': 'formal',
             'desc': 'Elegant designer wristwatch with leather strap.'},

            # Shop 4 — Style Emporium
            {'shop': shop4, 'cat': 'men', 'name': 'Polo T-Shirt', 'price': 999, 'type': 'casual',
             'desc': 'Classic polo t-shirt in premium cotton.'},
            {'shop': shop4, 'cat': 'women', 'name': 'Kurti Set', 'price': 1599, 'type': 'ethnic',
             'desc': 'Elegant kurti with palazzo set.'},
            {'shop': shop4, 'cat': 'footwear', 'name': 'Leather Shoes', 'price': 2200, 'type': 'formal',
             'desc': 'Genuine leather formal shoes.'},
            {'shop': shop4, 'cat': 'kids', 'name': 'Party Dress', 'price': 899, 'type': 'party',
             'desc': 'Cute party dress for girls with sequin work.'},
        ]

        colors = [
            ('Red', '#E53935'), ('Blue', '#1E88E5'), ('Black', '#212121'),
            ('White', '#FAFAFA'), ('Green', '#43A047'), ('Navy', '#1A237E'),
            ('Pink', '#EC407A'), ('Grey', '#757575'),
        ]
        sizes = ['S', 'M', 'L', 'XL']

        for pdata in products_data:
            product, created = Product.objects.get_or_create(
                name=pdata['name'],
                shop=pdata['shop'],
                defaults={
                    'category': categories[pdata['cat']],
                    'description': pdata['desc'],
                    'base_price': pdata['price'],
                    'product_type': pdata['type'],
                    'is_available': True,
                    'is_featured': pdata['price'] > 1500,
                }
            )

            if created:
                # Create variants (2 colors × 4 sizes = 8 variants per product)
                import random
                chosen_colors = random.sample(colors, 2)
                for color_name, color_code in chosen_colors:
                    for size in sizes:
                        ProductVariant.objects.create(
                            product=product,
                            size=size,
                            color=color_name,
                            color_code=color_code,
                            variant_type=pdata['type'],
                            stock_quantity=random.randint(3, 20),
                        )

        self.stdout.write(self.style.SUCCESS(f'✅ {len(products_data)} Products with variants created'))

        # ---- Summary ----
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 ShopNow seeded successfully!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   Users: {User.objects.count()}')
        self.stdout.write(f'   Vendors: {Vendor.objects.count()}')
        self.stdout.write(f'   Shops: {Shop.objects.count()}')
        self.stdout.write(f'   Categories: {Category.objects.count()}')
        self.stdout.write(f'   Products: {Product.objects.count()}')
        self.stdout.write(f'   Variants: {ProductVariant.objects.count()}')
        self.stdout.write(f'\n🔐 Login credentials:')
        self.stdout.write(f'   Admin:    admin / admin123')
        self.stdout.write(f'   Vendor 1: vendor1 / vendor123')
        self.stdout.write(f'   Vendor 2: vendor2 / vendor123')
        self.stdout.write(f'   Customer: ravi / customer123')
        self.stdout.write(f'   Customer: priya / customer123\n')
