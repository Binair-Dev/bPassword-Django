#!/usr/bin/env python3
import os
import django
import sys

# Ajouter le répertoire Django au path
sys.path.append('/home/coder/system/dev/bPassword-Django/bpassword')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bpassword.settings')

django.setup()

from django.contrib.auth.models import User

# Créer un superutilisateur par défaut
username = 'admin'
email = 'admin@bpassword.local'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superutilisateur créé:")
    print(f"   Nom d'utilisateur: {username}")
    print(f"   Email: {email}")
    print(f"   Mot de passe: {password}")
else:
    print("ℹ️  Un superutilisateur existe déjà")