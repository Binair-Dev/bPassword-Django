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

# Vérification et diagnostic des volumes
echo "📁 Vérification des volumes..."
ls -la /data /logs /backups

echo "🔍 Test d'écriture dans /data..."
if touch /data/test.txt 2>/dev/null; then
    echo "✅ Écriture OK dans /data"
    rm -f /data/test.txt
else
    echo "❌ ERREUR: Impossible d'écrire dans /data"
    whoami
    id
    ls -la /data
fi

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

# Diagnostic de la configuration Django
echo "🔧 Variables d'environnement Django:"
echo "DATABASE_URL = $DATABASE_URL"
echo "SECRET_KEY = ${SECRET_KEY:0:20}..."

# Test de connexion à la base
echo "💾 Test de connexion à la base de données..."
python manage.py shell -c "
from django.db import connection
from django.conf import settings
print('Database engine:', settings.DATABASES['default']['ENGINE'])
print('Database name:', settings.DATABASES['default']['NAME'])
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Connexion DB réussie')
except Exception as e:
    print('❌ ERREUR DB:', str(e))
    import os
    db_path = settings.DATABASES['default']['NAME']
    print('Chemin DB:', db_path)
    print('DB exists:', os.path.exists(db_path))
    print('DB dir exists:', os.path.exists(os.path.dirname(db_path)))
    print('DB dir perms:', oct(os.stat(os.path.dirname(db_path)).st_mode)[-3:])
"

echo "🚀 bPassword est prêt!"
echo "📱 Interface: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo ""

# Exécuter la commande passée en argument
exec "$@"