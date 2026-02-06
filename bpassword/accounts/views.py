from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django_otp import user_has_device
from django_otp.decorators import otp_required
from .security import LoginSecurityManager
from .totp import TOTPManager
from .validators import PasswordComplexityValidator
import logging

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('passwords')
    
    # Vérifier si le client est verrouillé
    if LoginSecurityManager.is_locked(request):
        remaining_time = LoginSecurityManager.get_lockout_remaining_time(request)
        if remaining_time:
            minutes = int(remaining_time.total_seconds() // 60)
            messages.error(request, f'Trop de tentatives de connexion échouées. Veuillez réessayer dans {minutes} minutes.')
        else:
            messages.error(request, 'Compte temporairement verrouillé pour des raisons de sécurité.')
        
        users_exist = User.objects.exists()
        return render(request, 'login.html', {'users_exist': users_exist, 'locked': True})
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validation de base
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
        elif len(username) > 150 or len(password) > 128:  # Limites Django
            messages.error(request, 'Données invalides.')
            LoginSecurityManager.record_failed_attempt(request)
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Connexion réussie - effacer les tentatives
                LoginSecurityManager.clear_attempts(request)
                login(request, user)
                
                # Log de sécurité
                logger = logging.getLogger('security')
                logger.info(f"Successful login for user: {username} from IP: {LoginSecurityManager._get_client_ip(request)}")
                
                # Vérifier si 2FA est activée
                if TOTPManager.is_2fa_enabled(user):
                    # Rediriger vers la vérification 2FA
                    next_url = request.GET.get('next', 'passwords')
                    return redirect(f'/accounts/verify-2fa/?next={next_url}')
                else:
                    # Connexion directe sans 2FA
                    next_url = request.GET.get('next', 'passwords')
                    return redirect(next_url)
            else:
                # Connexion échouée - enregistrer la tentative
                attempts_made = LoginSecurityManager.record_failed_attempt(request)
                remaining_attempts = LoginSecurityManager.get_remaining_attempts(request)
                
                # Log de sécurité
                logger = logging.getLogger('security')
                logger.warning(f"Failed login attempt for user: {username} from IP: {LoginSecurityManager._get_client_ip(request)} (Attempt {attempts_made})")
                
                if remaining_attempts > 0:
                    messages.error(request, f'Nom d\'utilisateur ou mot de passe incorrect. {remaining_attempts} tentative(s) restante(s).')
                else:
                    messages.error(request, 'Trop de tentatives échouées. Compte verrouillé pour 1 heure.')
    
    # Vérifier si des utilisateurs existent pour afficher le lien d'inscription
    users_exist = User.objects.exists()
    return render(request, 'login.html', {'users_exist': users_exist})

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('passwords')

    # Bloquer les inscriptions si un utilisateur existe déjà
    if User.objects.exists():
        messages.error(request, 'Les inscriptions sont fermées. Un utilisateur est déjà enregistré.')
        return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not all([username, password, password_confirm]):
            messages.error(request, 'Veuillez remplir tous les champs.')
        elif password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
            # Validation de complexité du mot de passe
            validator = PasswordComplexityValidator()
            try:
                validator.validate(password)
            except ValidationError as e:
                messages.error(request, e.message)
                return render(request, 'register.html')

            # Création de l'utilisateur
            try:
                user = User.objects.create_user(username=username, password=password)
                messages.success(request, 'Compte créé avec succès. Vous pouvez maintenant vous connecter.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Erreur lors de la création du compte.')

    return render(request, 'register.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')