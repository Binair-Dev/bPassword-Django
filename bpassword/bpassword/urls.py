from django.contrib import admin
from django.urls import include, path
from .views import index

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='index'),

    path('accounts/', include('accounts.urls')),
    path('passwords/', include('passwords.urls')),
    path('api/', include('api.urls')),
]
