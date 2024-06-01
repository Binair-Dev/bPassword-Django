from django.shortcuts import redirect, render

from .forms import CredentialForm
from .models import Credentials

# Create your views here.
def passwords(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            username = request.POST['username']
            password = request.POST['password']
            credential = Credentials.objects.create(name=name, username=username, password=password)
            credential.save()
            return redirect('passwords')
        search_query = request.GET.get('search', '')
        if search_query:
            credentials = Credentials.objects.filter(name__icontains=search_query)
        else:
            credentials = Credentials.objects.all()
        return render(request, 'passwords.html', {'credentials': credentials})
    return redirect('login')

def delete(request, id):
    credential = Credentials.objects.get(id=id)
    credential.delete()
    return redirect('passwords')

def update(request, id):
    credential = Credentials.objects.get(id=id)
    form = CredentialForm()
    if request.method == 'POST':
        credential.name = request.POST['name']
        credential.username = request.POST['username']
        credential.password = request.POST['password']
        credential.save()
        return redirect('passwords')
    if request.method == 'DELETE':
        credential.delete()
        return redirect('passwords')
    return render(request, 'update.html', {form: form, 'credential': credential})