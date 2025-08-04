#!/bin/bash

# Script pour nettoyer la base de données via Docker

set -e

echo "🧹 Nettoyage de la base de données bPassword via Docker"
echo "======================================================"

# Fonction pour détecter quel conteneur est en cours
detect_container() {
    if docker-compose -f docker-compose.simple.yml ps | grep -q "Up"; then
        echo "simple"
    elif docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        echo "dev"
    elif docker-compose ps | grep -q "Up"; then
        echo "prod"
    else
        echo "none"
    fi
}

# Détecter le mode actuel
MODE=$(detect_container)

case $MODE in
    "simple")
        COMPOSE_FILE="docker-compose.simple.yml"
        echo "📦 Conteneur détecté: Mode Simple"
        ;;
    "dev")
        COMPOSE_FILE="docker-compose.dev.yml"
        echo "📦 Conteneur détecté: Mode Développement"
        ;;
    "prod")
        COMPOSE_FILE="docker-compose.yml"
        echo "📦 Conteneur détecté: Mode Production"
        ;;
    "none")
        echo "❌ Aucun conteneur bPassword en cours d'exécution"
        echo "💡 Démarrez d'abord l'application:"
        echo "   ./docker-start.sh simple"
        exit 1
        ;;
esac

echo "🔧 Utilisation du fichier: $COMPOSE_FILE"

# Fonction de nettoyage des tables
reset_tables() {
    echo ""
    echo "🗑️  Suppression des données des tables..."
    
    # Nettoyer la table passwords_credentials
    docker-compose -f $COMPOSE_FILE exec web python -c "
import django
django.setup()
from passwords.models import Credentials
count = Credentials.objects.count()
print(f'📊 Identifiants trouvés: {count}')
if count > 0:
    deleted = Credentials.objects.all().delete()
    print(f'🗑️  Identifiants supprimés: {deleted[0]}')
else:
    print('✅ Table passwords_credentials déjà vide')
"

    # Nettoyer la table auth_user
    docker-compose -f $COMPOSE_FILE exec web python -c "
import django
django.setup()
from django.contrib.auth.models import User
count = User.objects.count()
print(f'📊 Utilisateurs trouvés: {count}')
if count > 0:
    deleted = User.objects.all().delete()
    print(f'🗑️  Utilisateurs supprimés: {deleted[0]}')
else:
    print('✅ Table auth_user déjà vide')
"
}

# Fonction pour créer un superutilisateur
create_superuser() {
    echo ""
    echo "👤 Création d'un nouveau superutilisateur..."
    
    docker-compose -f $COMPOSE_FILE exec web python -c "
import django
django.setup()
from django.contrib.auth.models import User

username = 'admin'
email = 'admin@bpassword.local'
password = 'admin123'

try:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Superutilisateur créé:')
    print(f'   Username: {username}')
    print(f'   Email: {email}')
    print(f'   Password: {password}')
except Exception as e:
    print(f'❌ Erreur: {e}')
"
}

# Afficher l'avertissement
echo ""
echo "⚠️  ATTENTION: Cette action va supprimer TOUTES les données !"
echo "   - Tous les identifiants sauvegardés"
echo "   - Tous les comptes utilisateurs"
echo "   - Cette action est IRRÉVERSIBLE"
echo ""

# Demander confirmation
read -p "🤔 Voulez-vous continuer ? (oui/non): " confirmation

case $confirmation in
    oui|OUI|o|O|yes|YES|y|Y)
        echo "🚀 Démarrage du nettoyage..."
        reset_tables
        
        echo ""
        read -p "💡 Créer un nouveau superutilisateur ? (oui/non): " create_user
        case $create_user in
            oui|OUI|o|O|yes|YES|y|Y)
                create_superuser
                ;;
            *)
                echo "ℹ️  Vous pourrez créer un superutilisateur plus tard avec:"
                echo "   docker-compose -f $COMPOSE_FILE exec web python manage.py createsuperuser"
                ;;
        esac
        
        echo ""
        echo "✅ Nettoyage terminé !"
        echo "🌐 Accédez à l'application: http://localhost:8150"
        ;;
    *)
        echo "❌ Nettoyage annulé."
        ;;
esac