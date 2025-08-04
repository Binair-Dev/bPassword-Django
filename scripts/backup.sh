#!/bin/bash

# Script de sauvegarde pour bPassword Django
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
POSTGRES_HOST="postgres"
POSTGRES_DB="bpassword"
POSTGRES_USER="bpassword_user"

echo "🔄 Démarrage de la sauvegarde - $TIMESTAMP"

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p $BACKUP_DIR

# Sauvegarde PostgreSQL
if pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER; then
    echo "📊 Sauvegarde de la base de données PostgreSQL..."
    BACKUP_FILE="$BACKUP_DIR/bpassword_backup_$TIMESTAMP.sql"
    
    PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
        -h $POSTGRES_HOST \
        -U $POSTGRES_USER \
        -d $POSTGRES_DB \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        > $BACKUP_FILE
    
    # Compresser la sauvegarde
    gzip $BACKUP_FILE
    echo "✅ Sauvegarde PostgreSQL créée: ${BACKUP_FILE}.gz"
else
    echo "⚠️  PostgreSQL non accessible, tentative de sauvegarde SQLite..."
    
    # Sauvegarde SQLite (si disponible)
    if [ -f "/app/bpassword/db.sqlite3" ]; then
        SQLITE_BACKUP="$BACKUP_DIR/bpassword_sqlite_$TIMESTAMP.db"
        cp /app/bpassword/db.sqlite3 $SQLITE_BACKUP
        gzip $SQLITE_BACKUP
        echo "✅ Sauvegarde SQLite créée: ${SQLITE_BACKUP}.gz"
    fi
fi

# Nettoyer les anciennes sauvegardes (garder les 7 dernières)
echo "🧹 Nettoyage des anciennes sauvegardes..."
cd $BACKUP_DIR
ls -t *.gz 2>/dev/null | tail -n +8 | xargs -r rm
echo "✅ Nettoyage terminé"

# Créer un fichier de log
LOG_FILE="$BACKUP_DIR/backup_log_$TIMESTAMP.txt"
cat > $LOG_FILE << EOF
Sauvegarde bPassword Django
==========================
Date: $(date)
Hostname: $(hostname)
Files created:
$(ls -la $BACKUP_DIR/*$TIMESTAMP*)

Database status:
$(pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER 2>&1 || echo "PostgreSQL non accessible")

Disk usage:
$(df -h $BACKUP_DIR)
EOF

echo "📝 Log créé: $LOG_FILE"
echo "✅ Sauvegarde terminée avec succès!"