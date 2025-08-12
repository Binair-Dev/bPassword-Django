from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django_otp import user_has_device
from accounts.totp import TOTPManager

def otp_required_if_enabled(view_func):
    """
    Décorateur qui exige la 2FA seulement si elle est activée pour l'utilisateur.
    Si la 2FA n'est pas activée, permet l'accès direct.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Si l'utilisateur n'a pas activé la 2FA, accès direct
        if not TOTPManager.is_2fa_enabled(request.user):
            return view_func(request, *args, **kwargs)
        
        # Si 2FA activée, vérifier si l'utilisateur est authentifié avec 2FA
        if not request.user.is_verified():
            # Rediriger vers la vérification 2FA
            next_url = request.get_full_path()
            return redirect(f'/accounts/verify-2fa/?next={next_url}')
        
        # Utilisateur vérifié avec 2FA, continuer
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view