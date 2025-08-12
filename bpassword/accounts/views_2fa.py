from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp import user_has_device
from .totp import TOTPManager

@csrf_protect
def verify_2fa(request):
    """Vue pour vérifier le code 2FA après connexion"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Si l'utilisateur est déjà vérifié, rediriger
    if request.user.is_verified():
        return redirect('passwords')
    
    # Si pas de 2FA configurée, rediriger
    if not TOTPManager.is_2fa_enabled(request.user):
        return redirect('passwords')
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if not token:
            messages.error(request, 'Veuillez entrer le code de vérification.')
        else:
            # Vérifier avec le device TOTP
            totp_device = TOTPManager.get_user_totp_device(request.user)
            if totp_device and totp_device.verify_token(token):
                # Marquer l'utilisateur comme vérifié pour cette session
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, request.user)
                request.session['otp_device_id'] = totp_device.persistent_id
                
                messages.success(request, 'Authentification réussie!')
                next_url = request.GET.get('next', 'passwords')
                return redirect(next_url)
            else:
                # Vérifier avec les codes de backup
                try:
                    static_device = StaticDevice.objects.get(user=request.user, name='backup')
                    if static_device.verify_token(token):
                        # Code de backup valide
                        request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, request.user)
                        request.session['otp_device_id'] = static_device.persistent_id
                        
                        messages.success(request, 'Authentification réussie avec code de backup!')
                        messages.warning(request, 'Code de backup utilisé. Il ne pourra plus être réutilisé.')
                        next_url = request.GET.get('next', 'passwords')
                        return redirect(next_url)
                except StaticDevice.DoesNotExist:
                    pass
                
                messages.error(request, 'Code de vérification incorrect.')
    
    return render(request, 'verify_2fa.html', {
        'backup_codes_available': len(TOTPManager.get_backup_codes(request.user)) > 0
    })