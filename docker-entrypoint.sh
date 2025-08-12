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

# Test des permissions sur le dossier /data AVANT les migrations
echo "🔐 Test complet des permissions..."
ls -la /data/
echo "📍 Tentative de création du fichier DB manuellement..."
if touch /data/db.sqlite3; then
    echo "✅ Fichier db.sqlite3 créé avec succès"
    ls -la /data/db.sqlite3
else
    echo "❌ Impossible de créer db.sqlite3"
fi

# Test direct avec Python/SQLite
echo "🐍 Test direct Python SQLite..."
python -c "
import sqlite3
import os
try:
    # Test de connexion SQLite directe
    conn = sqlite3.connect('/data/test.db')
    conn.execute('CREATE TABLE test (id INTEGER)')
    conn.close()
    print('✅ SQLite direct fonctionne')
    os.remove('/data/test.db')
except Exception as e:
    print('❌ SQLite direct échoue:', str(e))
"

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


echo "🚀 bPassword est prêt!"
echo "📱 Interface: http://localhost:8000"
echo "👨‍💼 Admin: http://localhost:8000/admin"
echo ""

# Exécuter la commande passée en argument
exec "$@"