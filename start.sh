#!/bin/bash

# Script de démarrage pour bPassword Django

echo "🔒 Démarrage de bPassword Django..."

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env manquant. Copie du template..."
    cp .env.example .env
    echo "✅ Fichier .env créé. Veuillez le configurer avant de continuer."
    echo "📝 Editez le fichier .env avec vos propres valeurs."
    exit 1
fi

# Aller dans le répertoire Django
cd bpassword

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
python3 -c "import django, cryptography, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dépendances manquantes. Installation..."
    pip3 install -r ../requirements.txt
fi

# Migrations
echo "🗄️  Application des migrations..."
python3 manage.py migrate

# Vérifier si un superutilisateur existe
echo "👤 Vérification du superutilisateur..."
python3 manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('Aucun superutilisateur trouvé.')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "🔑 Création d'un superutilisateur..."
    python3 manage.py createsuperuser
fi

# Démarrage du serveur
echo "🚀 Démarrage du serveur..."
echo "📱 Interface accessible sur : http://localhost:8000"
echo "👨‍💼 Admin accessible sur : http://localhost:8000/admin"
echo ""
echo "🔒 Fonctionnalités disponibles :"
echo "  - Connexion/Inscription : /accounts/login/"
echo "  - Gestionnaire de mots de passe : /passwords/"
echo "  - Export/Import JSON intégré"
echo "  - Chiffrement automatique des mots de passe"
echo ""

python3 manage.py runserver