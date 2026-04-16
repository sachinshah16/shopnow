from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.db.models import Sum
from .forms import CustomerRegistrationForm, VendorRegistrationForm, ProfileUpdateForm

User = get_user_model()


class RegisterCustomerView(View):
    """Customer registration."""

    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'users/register.html', {'form': form, 'role': 'customer'})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to ShopNow! Start shopping now.')
            return redirect('products:home')
        return render(request, 'users/register.html', {'form': form, 'role': 'customer'})


class RegisterVendorView(View):
    """Vendor registration."""

    def get(self, request):
        form = VendorRegistrationForm()
        return render(request, 'users/register.html', {'form': form, 'role': 'vendor'})

    def post(self, request):
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Vendor account created! Set up your shop now.')
            return redirect('vendors:dashboard')
        return render(request, 'users/register.html', {'form': form, 'role': 'vendor'})


class LoginView(View):
    """User login."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:dashboard')
        return render(request, 'users/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('users:dashboard')
        messages.error(request, 'Invalid username or password.')
        return render(request, 'users/login.html')


class LogoutView(View):
    """User logout."""

    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('products:home')


class DashboardRedirectView(LoginRequiredMixin, View):
    """Redirect to appropriate dashboard based on role."""

    def get(self, request):
        if request.user.role in ['vendor', 'admin', 'delivery'] or request.user.is_superuser:
            return redirect('users:mode_select')
        return redirect('products:home')


class ModeSelectView(LoginRequiredMixin, View):
    """Mode selection page for authorized roles to choose Dashboard or User mode."""
    
    def get(self, request):
        if not (request.user.role in ['vendor', 'admin', 'delivery'] or request.user.is_superuser):
            return redirect('products:home')
        return render(request, 'users/mode_select.html')


class ProfileView(LoginRequiredMixin, View):
    """View and edit user profile."""

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, 'users/profile.html', {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        return render(request, 'users/profile.html', {'form': form})


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin that restricts access to admin role users only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Admin access required.')
            return redirect('products:home')
        return super().dispatch(request, *args, **kwargs)


class AdminDashboardView(AdminRequiredMixin, View):
    """Platform-wide admin dashboard with aggregated stats."""

    def get(self, request):
        from orders.models import Order
        from products.models import Product
        from vendors.models import Vendor, Shop

        total_users = User.objects.count()
        total_vendors = User.objects.filter(role='vendor').count()
        total_products = Product.objects.count()
        total_shops = Shop.objects.count()
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        total_revenue = Order.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        recent_users = User.objects.order_by('-date_joined')[:8]

        context = {
            'total_users': total_users,
            'total_vendors': total_vendors,
            'total_products': total_products,
            'total_shops': total_shops,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'recent_users': recent_users,
        }
        return render(request, 'users/admin_dashboard.html', context)


class AdminOrdersView(AdminRequiredMixin, View):
    """Platform-wide order list for admin."""

    def get(self, request):
        from orders.models import Order
        status_filter = request.GET.get('status', '')
        orders = Order.objects.select_related('user').order_by('-created_at')
        if status_filter:
            orders = orders.filter(status=status_filter)
        return render(request, 'users/admin_orders.html', {
            'orders': orders,
            'status_filter': status_filter,
        })


class AdminUsersView(AdminRequiredMixin, View):
    """Platform-wide user list for admin."""

    def get(self, request):
        role_filter = request.GET.get('role', '')
        users = User.objects.order_by('-date_joined')
        if role_filter:
            users = users.filter(role=role_filter)
        return render(request, 'users/admin_users.html', {
            'users': users,
            'role_filter': role_filter,
        })


class AdminVendorsView(AdminRequiredMixin, View):
    """Vendor list for admin."""

    def get(self, request):
        from vendors.models import Vendor
        vendors = Vendor.objects.select_related('user').prefetch_related('shops').order_by('-created_at')
        return render(request, 'users/admin_vendors.html', {'vendors': vendors})
