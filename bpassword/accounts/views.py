from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('passwords')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'passwords')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
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
        elif len(password) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
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