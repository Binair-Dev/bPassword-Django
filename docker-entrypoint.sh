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

# Créer le dossier data pour SQLite
mkdir -p /app/data

# Se déplacer dans le répertoire Django
cd /app/bpassword || {
    echo "❌ Erreur: répertoire /app/bpassword introuvable"
    echo "Structure disponible:"
    ls -la /app/
    exit 1
}

# Appliquer les migrations
echo "🗄️  Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques (pour la production)
if [[ "$DEBUG" == "False" ]]; then
    echo "📁 Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput
fi

# Vérifier les utilisateurs existants (sans en créer)
echo "👤 Vérification des utilisateurs..."
python manage.py shell << EOF
from django.contrib.auth.models import User

user_count = User.objects.count()
if user_count == 0:
    print("ℹ️  Aucun utilisateur dans la base de données")
    print("📝 Utilisez l'interface d'inscription pour créer des comptes")
else:
    print(f"ℹ️  {user_count} utilisateur(s) trouvé(s) dans la base")
EOF

echo "🚀 bPassword est prêt!"
echo "📱 Interface: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo ""

# Exécuter la commande passée en argument
exec "$@"