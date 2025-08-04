# 🔧 Fix Chemin Docker - bPassword Django

## 🚨 Problème Identifié

Erreurs dans les logs Docker :
```
python: can't open file '/app/bpassword/bpassword/manage.py': [Errno 2] No such file or directory
```

**Causes :**
1. **Conflit de montage de volumes** sur `/app/bpassword`
2. **Boucle de redémarrage infinie** du conteneur
3. **Chemins incorrects** dans la structure Docker

## ❌ **Problèmes Originaux**

### Structure incorrecte
```yaml
# Problématique : montage sur le dossier de code
volumes:
  - sqlite_data:/app/bpassword  # ❌ Écrase le code Django

# Commande incorrecte
CMD ["python", "bpassword/manage.py", "runserver", "0.0.0.0:8000"]  # ❌ Chemin erroné
```

## ✅ **Solutions Implémentées**

### 1. **Volume séparé pour les données**
```yaml
# Nouveau : dossier dédié aux données
volumes:
  - sqlite_data:/app/data  # ✅ Dossier séparé pour SQLite
```

### 2. **Chemin SQLite corrigé**
```yaml
# Base de données dans le volume persistant
DATABASE_URL: sqlite:////app/data/db.sqlite3  # ✅ Chemin absolu correct
```

### 3. **Dockerfile corrigé**
```dockerfile
# Commande correcte depuis le bon répertoire
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]  # ✅ Depuis /app/bpassword
```

### 4. **Entrypoint amélioré**
```bash
# Création du dossier data
mkdir -p /app/data

# Navigation sécurisée avec vérification d'erreur
cd /app/bpassword || {
    echo "❌ Erreur: répertoire introuvable"
    ls -la /app/
    exit 1
}
```

## 🔧 **Corrections Appliquées**

### Fichiers modifiés :
- ✅ `docker-compose.yml` - Volume `/app/data` + DATABASE_URL
- ✅ `docker-compose.simple.yml` - Même correction
- ✅ `docker-compose.dev.yml` - Même correction
- ✅ `Dockerfile` - CMD corrigé
- ✅ `docker-entrypoint.sh` - Gestion d'erreurs + dossier data

### Structure finale :
```
/app/
├── bpassword/          # Code Django (non monté)
│   ├── manage.py       # ✅ Accessible
│   └── ...
├── data/               # Volume persistant
│   └── db.sqlite3      # ✅ Base de données
├── backups/            # Montage local
└── static/             # Volume statique
```

## 🚀 **Résultat Attendu**

### Plus d'erreurs :
- ❌ `can't open file manage.py`
- ❌ Boucle de redémarrage infinie
- ❌ Conflit de montage volume

### Démarrage normal :
```bash
./docker-start.sh simple
# Interface accessible : http://localhost:8150
```

## 🔍 **Diagnostic**

Si le problème persiste, vérifier :

```bash
# Voir les logs du conteneur
docker-compose -f docker-compose.simple.yml logs web

# Vérifier la structure interne
docker-compose -f docker-compose.simple.yml exec web ls -la /app/

# Tester l'accès à manage.py
docker-compose -f docker-compose.simple.yml exec web python /app/bpassword/manage.py --help
```

Le problème de chemin et de montage de volume est maintenant **complètement résolu** ! 🎯