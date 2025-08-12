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

# Les dossiers sont créés dans le Dockerfile avec les bonnes permissions
echo "📁 Vérification des volumes..."
ls -la /data /logs /backups 2>/dev/null || echo "⚠️  Volumes non montés correctement"

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

# Vérifier l'état de la base de données
echo "💾 Vérification de la base de données..."
if [ -f "/data/db.sqlite3" ]; then
    echo "✅ Base de données existante trouvée - conservation des données"
    # Vérifier les utilisateurs existants
    python manage.py shell -c "
from django.contrib.auth.models import User
user_count = User.objects.count()
print(f'ℹ️  {user_count} utilisateur(s) dans la base existante')
"
else
    echo "🆕 Nouvelle installation - base de données sera créée"
    echo "📝 Utilisez l'interface d'inscription pour créer des comptes"
fi

echo "🚀 bPassword est prêt!"
echo "📱 Interface: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo ""

# Exécuter la commande passée en argument
exec "$@"