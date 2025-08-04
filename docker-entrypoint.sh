#!/bin/bash
set -e

echo "🐳 Démarrage de bPassword Django..."

# Attendre que la base de données soit prête
if [[ "$DATABASE_URL" == postgres* ]]; then
    echo "⏳ Attente de la base de données PostgreSQL..."
    while ! pg_isready -h postgres -p 5432 -U bpassword_user; do
        echo "PostgreSQL n'est pas encore prêt - attente..."
        sleep 2
    done
    echo "✅ PostgreSQL est prêt!"
fi

# Se déplacer dans le répertoire Django
cd /app/bpassword

# Appliquer les migrations
echo "🗄️  Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques (pour la production)
if [[ "$DEBUG" == "False" ]]; then
    echo "📁 Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput
fi

# Créer un superutilisateur par défaut si aucun n'existe
echo "👤 Vérification du superutilisateur..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@bpassword.local')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superutilisateur créé: {username}")
else:
    print(f"ℹ️  Superutilisateur existe déjà: {username}")
EOF

echo "🚀 bPassword est prêt!"
echo "📱 Interface: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo ""

# Exécuter la commande passée en argument
exec "$@"