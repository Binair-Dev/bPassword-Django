import qrcode
import io
import base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.util import random_hex
from django.urls import reverse

class TOTPManager:
    """Gestionnaire pour l'authentification TOTP (Google Authenticator)"""
    
    @staticmethod
    def get_user_totp_device(user, create_if_not_exists=False):
        """Récupère ou crée le device TOTP de l'utilisateur"""
        try:
            device = TOTPDevice.objects.get(user=user, name='default')
        except TOTPDevice.DoesNotExist:
            if create_if_not_exists:
                device = TOTPDevice.objects.create(
                    user=user,
                    name='default',
                    confirmed=False
                )
            else:
                device = None
        return device
    
    @staticmethod
    def get_user_static_device(user, create_if_not_exists=False):
        """Récupère ou crée le device pour codes de backup"""
        try:
            device = StaticDevice.objects.get(user=user, name='backup')
        except StaticDevice.DoesNotExist:
            if create_if_not_exists:
                device = StaticDevice.objects.create(
                    user=user,
                    name='backup',
                    confirmed=True
                )
                # Créer 10 codes de backup
                for _ in range(10):
                    StaticToken.objects.create(
                        device=device,
                        token=random_hex()[:8].upper()
                    )
            else:
                device = None
        return device
    
    @staticmethod
    def generate_qr_code(device, request):
        """Génère le QR code pour Google Authenticator"""
        # Configuration de l'URL TOTP
        issuer_name = "bPassword"
        account_name = f"{issuer_name} ({device.user.username})"
        
        # URL au format standard TOTP
        totp_url = device.config_url
        
        # Personnaliser l'URL avec le nom de l'application
        if 'issuer=' not in totp_url:
            separator = '&' if '?' in totp_url else '?'
            totp_url += f"{separator}issuer={issuer_name}"
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=4,
        )
        qr.add_data(totp_url)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64 pour affichage dans le template
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_code_data
    
    @staticmethod
    def is_2fa_enabled(user):
        """Vérifie si la 2FA est activée pour l'utilisateur"""
        try:
            device = TOTPDevice.objects.get(user=user, name='default')
            return device.confirmed
        except TOTPDevice.DoesNotExist:
            return False
    
    @staticmethod
    def get_backup_codes(user):
        """Récupère les codes de backup disponibles"""
        try:
            device = StaticDevice.objects.get(user=user, name='backup')
            return [token.token for token in device.token_set.all()]
        except StaticDevice.DoesNotExist:
            return []

@login_required
@csrf_protect
def setup_2fa(request):
    """Vue pour configurer la 2FA"""
    user = request.user
    
    # Vérifier si 2FA déjà activée
    if TOTPManager.is_2fa_enabled(user):
        messages.info(request, 'La double authentification est déjà activée.')
        return redirect('account_security')
    
    # Récupérer ou créer le device TOTP
    device = TOTPManager.get_user_totp_device(user, create_if_not_exists=True)
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if not token:
            messages.error(request, 'Veuillez entrer le code de vérification.')
        elif device.verify_token(token):
            # Confirmer le device
            device.confirmed = True
            device.save()
            
            # Créer les codes de backup
            TOTPManager.get_user_static_device(user, create_if_not_exists=True)
            
            messages.success(request, 'Double authentification activée avec succès!')
            return redirect('account_security')
        else:
            messages.error(request, 'Code de vérification incorrect. Réessayez.')
    
    # Générer le QR code
    qr_code = TOTPManager.generate_qr_code(device, request)
    
    return render(request, 'setup_2fa.html', {
        'qr_code': qr_code,
        'secret_key': device.key,
        'app_name': 'bPassword',
        'username': user.username
    })

@login_required 
@csrf_protect
def disable_2fa(request):
    """Vue pour désactiver la 2FA"""
    if request.method == 'POST':
        # Supprimer tous les devices de l'utilisateur
        TOTPDevice.objects.filter(user=request.user).delete()
        StaticDevice.objects.filter(user=request.user).delete()
        
        messages.success(request, 'Double authentification désactivée.')
    
    return redirect('account_security')

@login_required
def backup_codes(request):
    """Vue pour afficher les codes de backup"""
    user = request.user
    
    if not TOTPManager.is_2fa_enabled(user):
        messages.error(request, 'La double authentification n\'est pas activée.')
        return redirect('account_security')
    
    codes = TOTPManager.get_backup_codes(user)
    
    return render(request, 'backup_codes.html', {
        'backup_codes': codes
    })

@login_required
def account_security(request):
    """Vue principale des paramètres de sécurité"""
    user = request.user
    is_2fa_enabled = TOTPManager.is_2fa_enabled(user)
    backup_codes_count = len(TOTPManager.get_backup_codes(user)) if is_2fa_enabled else 0
    
    return render(request, 'account_security.html', {
        'is_2fa_enabled': is_2fa_enabled,
        'backup_codes_count': backup_codes_count
    })