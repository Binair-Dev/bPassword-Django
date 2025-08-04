# 🔄 Redémarrage Requis - bPassword Django

## 🚨 Problème Persistant

L'erreur ALLOWED_HOSTS persiste malgré les corrections :
```
DisallowedHost at /
Invalid HTTP_HOST header: '192.168.0.249:8150'. 
You may need to add '192.168.0.249' to ALLOWED_HOSTS.
```

## 🔍 **Cause**

**Le conteneur Docker tourne encore avec l'ancienne configuration !**

Les modifications dans `docker-compose.yml` ne sont pas appliquées car le conteneur n'a pas été redémarré depuis les changements.

## ✅ **Solution : Redémarrage Forcé**

### 1. **Arrêter tous les conteneurs bPassword**
```bash
# Arrêter mode simple
docker-compose -f docker-compose.simple.yml down

# Arrêter mode prod  
docker-compose down

# Arrêter mode dev
docker-compose -f docker-compose.dev.yml down

# Ou arrêter tout avec le script
./docker-start.sh stop
```

### 2. **Nettoyer les conteneurs existants**
```bash
# Voir les conteneurs bPassword
docker ps -a | grep bpassword

# Supprimer les conteneurs anciens
docker rm -f $(docker ps -aq --filter name=bpassword)

# Optionnel : nettoyer les images
docker rmi $(docker images --filter reference="*bpassword*" -q)
```

### 3. **Redémarrer avec nouvelle configuration**
```bash
# Reconstruire et démarrer
./docker-start.sh build
./docker-start.sh simple

# Ou manuellement
docker-compose -f docker-compose.simple.yml up --build -d
```

## 🔧 **Configuration Mise à Jour**

### Double sécurité appliquée :

**1. Variables d'environnement Docker :**
```yaml
ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0,web,192.168.0.249,*
```

**2. Valeur par défaut Django (settings.py) :**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,*').split(',')
```

## 🎯 **Vérification**

Après redémarrage, vérifier :

```bash
# Voir les logs en temps réel
docker-compose -f docker-compose.simple.yml logs -f web

# Tester l'accès
curl -I http://192.168.0.249:8150

# Vérifier la configuration dans le conteneur
docker-compose -f docker-compose.simple.yml exec web python -c "
import os
print('ALLOWED_HOSTS:', os.getenv('ALLOWED_HOSTS'))
"
```

## 🚨 **Actions Requises**

### **VOUS DEVEZ REDÉMARRER LE CONTENEUR :**

1. **Arrêter** : `./docker-start.sh stop`
2. **Reconstruire** : `./docker-start.sh build` 
3. **Redémarrer** : `./docker-start.sh simple`

Ou en une commande :
```bash
./docker-start.sh stop && ./docker-start.sh simple
```

## ✅ **Résultat Attendu**

Après redémarrage **FORCÉ** :
- ✅ http://192.168.0.249:8150 → **Page de connexion bPassword**
- ❌ Plus d'erreur DisallowedHost
- ✅ Accès depuis toutes les IPs du réseau

**Le conteneur DOIT être redémarré pour que les changements prennent effet !** 🔄