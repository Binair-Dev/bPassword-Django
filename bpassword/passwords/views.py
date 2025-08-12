from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required
from .decorators import otp_required_if_enabled
from django.contrib import messages
import json
import re
from django.core import serializers

from .forms import CredentialForm
from .models import Credentials

# Create your views here.
def _validate_credential_input(name, username, password):
    """Valide les données d'entrée pour les credentials"""
    errors = []
    
    # Validation des longueurs
    if len(name) > 255:
        errors.append("Le nom ne peut pas dépasser 255 caractères.")
    if len(username) > 255:
        errors.append("Le nom d'utilisateur ne peut pas dépasser 255 caractères.")
    if len(password) > 1000:  # Limite raisonnable avant chiffrement
        errors.append("Le mot de passe est trop long.")
    
    # Validation des caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        if char in name or char in username:
            errors.append("Caractères non autorisés détectés.")
            break
    
    # Validation avec regex pour éviter les injections
    if not re.match(r'^[a-zA-Z0-9\s\-_\.@]+$', name) and name:
        errors.append("Le nom contient des caractères non autorisés.")
    if not re.match(r'^[a-zA-Z0-9\s\-_\.@]+$', username) and username:
        errors.append("Le nom d'utilisateur contient des caractères non autorisés.")
    
    return errors

@otp_required_if_enabled
def passwords(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            
            # Validation de base
            if not all([name, username, password]):
                messages.error(request, 'Tous les champs sont obligatoires.')
                return redirect('passwords')
            
            # Validation avancée
            validation_errors = _validate_credential_input(name, username, password)
            if validation_errors:
                for error in validation_errors:
                    messages.error(request, error)
                return redirect('passwords')
            
            # Vérifier les doublons
            if Credentials.objects.filter(user=request.user, name=name, username=username).exists():
                messages.warning(request, 'Un identifiant avec ce nom et nom d\'utilisateur existe déjà.')
                return redirect('passwords')
            
            credential = Credentials.objects.create(
                user=request.user,
                name=name, 
                username=username, 
                password=password
            )
            messages.success(request, f'Identifiant "{name}" ajouté avec succès.')
            return redirect('passwords')
            
        except Exception as e:
            messages.error(request, 'Erreur lors de l\'ajout de l\'identifiant.')
            return redirect('passwords')
    
    # Validation de la recherche
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Limiter la longueur de recherche et valider
        if len(search_query) > 100:
            search_query = search_query[:100]
        
        # Échapper les caractères spéciaux pour éviter les injections
        search_query = re.sub(r'[<>"\'\&]', '', search_query)
        
        credentials = Credentials.objects.filter(
            user=request.user,
            name__icontains=search_query
        )
    else:
        credentials = Credentials.objects.filter(user=request.user)
    
    return render(request, 'passwords.html', {'credentials': credentials})

@otp_required_if_enabled
def delete(request, id):
    try:
        credential = get_object_or_404(Credentials, id=id, user=request.user)
        credential.delete()
    except Exception as e:
        # TODO: Ajouter logging
        pass
    return redirect('passwords')

@otp_required_if_enabled
def update(request, id):
    try:
        # Validation de l'ID
        try:
            credential_id = int(id)
        except (ValueError, TypeError):
            messages.error(request, 'Identifiant invalide.')
            return redirect('passwords')
        
        credential = get_object_or_404(Credentials, id=credential_id, user=request.user)
        form = CredentialForm()
        
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            
            # Validation de base
            if not all([name, username, password]):
                messages.error(request, 'Tous les champs sont obligatoires.')
                return redirect('update', id=credential_id)
            
            # Validation avancée
            validation_errors = _validate_credential_input(name, username, password)
            if validation_errors:
                for error in validation_errors:
                    messages.error(request, error)
                return redirect('update', id=credential_id)
            
            # Vérifier les doublons (sauf pour l'enregistrement actuel)
            duplicate = Credentials.objects.filter(
                user=request.user, 
                name=name, 
                username=username
            ).exclude(id=credential_id).exists()
            
            if duplicate:
                messages.warning(request, 'Un identifiant avec ce nom et nom d\'utilisateur existe déjà.')
                return redirect('update', id=credential_id)
            
            credential.name = name
            credential.username = username
            credential.password = password
            credential.save()
            messages.success(request, f'Identifiant "{name}" mis à jour avec succès.')
            return redirect('passwords')
        
        if request.method == 'DELETE':
            credential.delete()
            messages.success(request, 'Identifiant supprimé avec succès.')
            return redirect('passwords')
        
        # Décrypter le mot de passe pour l'affichage
        credential.decrypted_password = credential.get_decrypted_password()
        return render(request, 'update.html', {'form': form, 'credential': credential})
        
    except Exception as e:
        messages.error(request, 'Erreur lors de la modification de l\'identifiant.')
        return redirect('passwords')

@otp_required_if_enabled
def export_credentials(request):
    credentials = Credentials.objects.filter(user=request.user)
    data = []
    
    for cred in credentials:
        data.append({
            'name': cred.name,
            'username': cred.username,
            'password': cred.get_decrypted_password()  # Exporter en clair pour la portabilité
        })
    
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="credentials_export.json"'
    return response

@csrf_exempt
@otp_required_if_enabled
def import_credentials(request):
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)
            
            uploaded_file = request.FILES['file']
            
            if not uploaded_file.name.endswith('.json'):
                return JsonResponse({'error': 'Le fichier doit être au format JSON'}, status=400)
            
            # Limite de taille de fichier (5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                return JsonResponse({'error': 'Fichier trop volumineux (max 5MB)'}, status=400)
            
            file_content = uploaded_file.read().decode('utf-8')
            credentials_data = json.loads(file_content)
            
            if not isinstance(credentials_data, list):
                return JsonResponse({'error': 'Le JSON doit contenir un tableau'}, status=400)
            
            imported_count = 0
            for cred_data in credentials_data:
                if isinstance(cred_data, dict) and all(key in cred_data for key in ['name', 'username', 'password']):
                    # Validation des données
                    name = str(cred_data['name']).strip()[:255]
                    username = str(cred_data['username']).strip()[:255]
                    password = str(cred_data['password']).strip()
                    
                    if all([name, username, password]):
                        credential = Credentials.objects.create(
                            user=request.user,
                            name=name,
                            username=username,
                            password=password
                        )
                        imported_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'{imported_count} identifiants importés avec succès'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de l\'importation: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)