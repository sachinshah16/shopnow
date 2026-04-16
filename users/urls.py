from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterCustomerView.as_view(), name='register_customer'),
    path('register/vendor/', views.RegisterVendorView.as_view(), name='register_vendor'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    path('mode/', views.ModeSelectView.as_view(), name='mode_select'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # Admin panel URLs
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/orders/', views.AdminOrdersView.as_view(), name='admin_orders'),
    path('admin-panel/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin-panel/vendors/', views.AdminVendorsView.as_view(), name='admin_vendors'),
]
