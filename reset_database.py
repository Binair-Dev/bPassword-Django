#!/usr/bin/env python3
"""
Script pour nettoyer la base de données bPassword Django
Supprime toutes les données des tables passwords_credentials et auth_user
"""
import os
import django
import sys

# Ajouter le répertoire Django au path
sys.path.append('/home/coder/system/dev/bPassword-Django/bpassword')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bpassword.settings')

django.setup()

from django.contrib.auth.models import User
from passwords.models import Credentials

def reset_database():
    """Nettoyer les tables principales"""
    print("🧹 Nettoyage de la base de données bPassword...")
    
    # Compter les données existantes
    users_count = User.objects.count()
    credentials_count = Credentials.objects.count()
    
    print(f"📊 Données existantes:")
    print(f"   - Utilisateurs (auth_user): {users_count}")
    print(f"   - Identifiants (passwords_credentials): {credentials_count}")
    
    if users_count == 0 and credentials_count == 0:
        print("✅ Base de données déjà vide !")
        return
    
    # Confirmation
    confirmation = input("\n⚠️  Voulez-vous vraiment supprimer TOUTES les données ? (oui/non): ")
    if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Nettoyage annulé.")
        return
    
    try:
        # Supprimer tous les identifiants
        credentials_deleted = Credentials.objects.all().delete()
        print(f"🗑️  Identifiants supprimés: {credentials_deleted[0]} entrées")
        
        # Supprimer tous les utilisateurs
        users_deleted = User.objects.all().delete()
        print(f"🗑️  Utilisateurs supprimés: {users_deleted[0]} entrées")
        
        print("\n✅ Base de données nettoyée avec succès !")
        print("💡 Vous pouvez maintenant recréer un superutilisateur:")
        print("   python manage.py createsuperuser")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False
    
    return True

def create_fresh_superuser():
    """Créer un nouveau superutilisateur après nettoyage"""
    print("\n👤 Création d'un nouveau superutilisateur...")
    
    username = 'admin'
    email = 'admin@bpassword.local'
    password = 'admin123'
    
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superutilisateur créé:")
        print(f"   Nom d'utilisateur: {username}")
        print(f"   Email: {email}")
        print(f"   Mot de passe: {password}")
        return True
    except Exception as e:
        print(f"❌ Erreur création superutilisateur: {e}")
        return False

if __name__ == "__main__":
    print("🔒 Script de nettoyage bPassword Django")
    print("=" * 50)
    
    # Nettoyer la base de données
    reset_database()
    
    print("\n🎯 Nettoyage terminé !")
    print("💡 Base de données complètement vide - aucun utilisateur créé")
    print("📝 Utilisez l'interface d'inscription pour créer de nouveaux comptes")