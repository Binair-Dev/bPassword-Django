from django.urls import path
from .views import login_view, logout_view, register_view
from . import views_2fa
from .totp import setup_2fa, disable_2fa, backup_codes, account_security

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    
    # 2FA URLs
    path('verify-2fa/', views_2fa.verify_2fa, name='verify_2fa'),
    path('setup-2fa/', setup_2fa, name='setup_2fa'),
    path('disable-2fa/', disable_2fa, name='disable_2fa'),
    path('backup-codes/', backup_codes, name='backup_codes'),
    path('security/', account_security, name='account_security'),
]
