from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import SplashView
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', SplashView.as_view(), name='splash'),
    path('home/', include('products.urls')),
    path('users/', include('users.urls')),
    path('vendor/', include('vendors.urls')),
    path('orders/', include('orders.urls')),
    path('keep-awaik/', lambda r:HttpResponse("working"))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
