from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers

from .forms import CredentialForm
from .models import Credentials

# Create your views here.
@login_required
def passwords(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            
            if not all([name, username, password]):
                # TODO: Ajouter message d'erreur dans le template
                return redirect('passwords')
            
            credential = Credentials.objects.create(
                user=request.user,
                name=name, 
                username=username, 
                password=password
            )
            return redirect('passwords')
        except Exception as e:
            # TODO: Ajouter logging et message d'erreur
            return redirect('passwords')
    
    search_query = request.GET.get('search', '')
    if search_query:
        credentials = Credentials.objects.filter(
            user=request.user,
            name__icontains=search_query
        )
    else:
        credentials = Credentials.objects.filter(user=request.user)
    
    return render(request, 'passwords.html', {'credentials': credentials})

@login_required
def delete(request, id):
    try:
        credential = get_object_or_404(Credentials, id=id, user=request.user)
        credential.delete()
    except Exception as e:
        # TODO: Ajouter logging
        pass
    return redirect('passwords')

@login_required
def update(request, id):
    try:
        credential = get_object_or_404(Credentials, id=id, user=request.user)
        form = CredentialForm()
        
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            
            if all([name, username, password]):
                credential.name = name
                credential.username = username
                credential.password = password
                credential.save()
            return redirect('passwords')
        
        if request.method == 'DELETE':
            credential.delete()
            return redirect('passwords')
        
        # Décrypter le mot de passe pour l'affichage
        credential.decrypted_password = credential.get_decrypted_password()
        return render(request, 'update.html', {'form': form, 'credential': credential})
    except Exception as e:
        # TODO: Ajouter logging
        return redirect('passwords')

@login_required
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
@login_required
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