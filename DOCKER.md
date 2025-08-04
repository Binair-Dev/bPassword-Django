# 🐳 Installation Docker - bPassword Django

## 🚀 Démarrage Rapide

### Option 1: Mode Développement (Recommandé pour débuter)
```bash
# Démarrage simple avec SQLite
./docker-start.sh dev
```

### Option 2: Mode Production (PostgreSQL + sécurité)
```bash
# Configuration puis démarrage
cp .env.example .env
# Éditer .env avec vos valeurs
./docker-start.sh prod
```

## 📋 Prérequis

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM libre
- 5GB espace disque

## 🛠️ Installation Complète

### Étape 1: Cloner et préparer
```bash
git clone <repo>
cd bPassword-Django
chmod +x docker-start.sh
```

### Étape 2: Configuration
```bash
# Copier le template de configuration
cp .env.example .env

# Éditer les variables (optionnel pour développement)
nano .env
```

### Étape 3: Démarrage
```bash
# Mode développement (SQLite + Debug)
./docker-start.sh dev

# OU Mode production (PostgreSQL + sécurité)
./docker-start.sh prod
```

## 🎯 Modes de Déploiement

### 🔧 Mode Développement
- **Base de données**: SQLite
- **Debug**: Activé  
- **Hot-reload**: Oui
- **SSL**: Désactivé
- **Commande**: `./docker-start.sh dev`

**Services démarrés:**
- `bpassword_dev` (port 8000)

### 🏭 Mode Production
- **Base de données**: PostgreSQL
- **Debug**: Désactivé
- **SSL**: Configuré
- **Sauvegardes**: Automatiques
- **Commande**: `./docker-start.sh prod`

**Services démarrés:**
- `bpassword_web` (port 8000)
- `bpassword_postgres` (port 5432)
- `bpassword_nginx` (ports 80/443) - optionnel

## 🔧 Commandes Utiles

```bash
# Voir les logs en temps réel
./docker-start.sh logs

# Ouvrir un shell dans le conteneur
./docker-start.sh shell

# Effectuer une sauvegarde
./docker-start.sh backup

# Reconstruire les images
./docker-start.sh build

# Arrêter tous les services
./docker-start.sh stop

# Nettoyer complètement
./docker-start.sh clean
```

## 📁 Structure des Fichiers Docker

```
bPassword-Django/
├── Dockerfile                 # Image principale
├── docker-compose.yml         # Production complète
├── docker-compose.dev.yml     # Développement simple
├── docker-entrypoint.sh       # Script d'initialisation
├── docker-start.sh            # Script de gestion
├── .dockerignore              # Fichiers à ignorer
├── nginx/
│   └── nginx.conf             # Configuration proxy
├── scripts/
│   └── backup.sh              # Script de sauvegarde
└── backups/                   # Dossier des sauvegardes
```

## 🔐 Configuration Sécurisée

### Variables d'environnement (.env)
```env
# Sécurité
SECRET_KEY=votre-clé-super-secrète-unique
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,localhost

# Base de données
DATABASE_URL=postgres://user:password@postgres:5432/bpassword

# Superutilisateur (optionnel)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@votre-domaine.com
DJANGO_SUPERUSER_PASSWORD=mot-de-passe-fort
```

### Certificats SSL (Production)
```bash
# Créer le dossier SSL
mkdir -p nginx/ssl

# Générer un certificat auto-signé (développement)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# Activer Nginx avec SSL
docker-compose --profile production up nginx -d
```

## 💾 Sauvegardes

### Sauvegarde Automatique
```bash
# Sauvegarde manuelle
./docker-start.sh backup

# Programmation avec cron (exemple)
0 2 * * * cd /path/to/bpassword && ./docker-start.sh backup
```

### Restauration
```bash
# Lister les sauvegardes
ls -la backups/

# Restaurer PostgreSQL
docker-compose exec postgres psql -U bpassword_user -d bpassword < backups/backup.sql

# Restaurer SQLite
cp backups/bpassword_sqlite_YYYYMMDD.db bpassword/db.sqlite3
```

## 📊 Monitoring et Logs

### Affichage des logs
```bash
# Tous les services
./docker-start.sh logs

# Service spécifique
docker-compose logs -f web
docker-compose logs -f postgres
```

### Vérification de l'état
```bash
# Status des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats

# Santé des services
docker-compose exec web curl http://localhost:8000/accounts/login/
```

## 🚨 Dépannage

### Erreurs Courantes

#### Port 8000 déjà utilisé
```bash
# Vérifier les processus
lsof -i :8000
# Arrêter le service ou changer le port dans docker-compose.yml
```

#### Base de données inaccessible
```bash
# Vérifier PostgreSQL
docker-compose exec postgres pg_isready
# Recréer le volume si nécessaire
docker-compose down -v && docker-compose up -d
```

#### Permissions Django
```bash
# Réinitialiser les migrations
docker-compose exec web python manage.py migrate --fake-initial
# Recréer le superutilisateur
docker-compose exec web python manage.py createsuperuser
```

### Nettoyage en cas de problème
```bash
# Arrêt complet et nettoyage
./docker-start.sh stop
./docker-start.sh clean

# Redémarrage à partir de zéro
./docker-start.sh build
./docker-start.sh dev
```

## 🌐 Accès aux Services

Une fois démarré, accédez aux services :

- **Interface principale**: http://localhost:8000
- **Administration Django**: http://localhost:8000/admin
- **API REST**: http://localhost:8000/api/ (si configurée)

### Comptes par défaut

**Mode développement:**
- Utilisateur: `admin`
- Mot de passe: `admin123`

**Mode production:**
- Configuré via variables d'environnement
- Ou créé manuellement: `docker-compose exec web python manage.py createsuperuser`

## 🔄 Mise à Jour

```bash
# Arrêter les services
./docker-start.sh stop

# Récupérer les modifications
git pull

# Reconstruire et redémarrer
./docker-start.sh build
./docker-start.sh prod  # ou dev
```

## 📈 Optimisations Production

### Performance
- Utiliser PostgreSQL au lieu de SQLite
- Activer Nginx comme proxy inverse
- Configurer Redis pour le cache (optionnel)
- Utiliser un CDN pour les fichiers statiques

### Sécurité
- Certificats SSL valides (Let's Encrypt)
- Firewall configuré (UFW)
- Sauvegardes automatiques
- Monitoring des logs
- Mise à jour régulière des images Docker

## 📞 Support

En cas de problème :

1. Vérifier les logs: `./docker-start.sh logs`
2. Consulter la documentation Django
3. Vérifier la configuration `.env`
4. Tester en mode développement d'abord

L'installation Docker de bPassword est maintenant prête pour le développement et la production ! 🚀