# 🌐 Configuration HTTP pour bPassword Django

## ✅ Modifications Appliquées pour HTTP

L'application a été configurée pour fonctionner en **HTTP** au lieu de HTTPS :

### 🔧 **Changements Django (`settings.py`)**
```python
# Désactivation des redirections HTTPS
SECURE_SSL_REDIRECT = False

# Pas de HSTS en HTTP
SECURE_HSTS_SECONDS = 0

# Cookies compatibles HTTP
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# SameSite plus flexible pour HTTP
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

### 🐳 **Docker Configuration**
- Port changé : `8000:8000` (au lieu de 8150)
- Nginx configuré pour HTTP uniquement
- Pas de redirection HTTPS automatique

### 🚀 **Utilisation**

**Mode développement (recommandé) :**
```bash
./docker-start.sh dev
# Interface : http://localhost:8000
```

**Mode production HTTP :**
```bash
./docker-start.sh prod
# Interface : http://localhost:8150
# Avec Nginx : http://localhost:80
```

### ⚠️ **Sécurité en HTTP**

**Limitations de sécurité en HTTP :**
- Données transmises en clair (non chiffrées)
- Cookies moins sécurisés
- Vulnérable aux attaques man-in-the-middle
- Pas de protection HSTS

**Recommandations :**
- ✅ **OK pour développement local**
- ✅ **OK pour réseaux internes sécurisés**
- ❌ **ÉVITER en production internet**

### 🔒 **Pour Revenir à HTTPS**

Si vous voulez réactiver HTTPS plus tard :

1. **Modifier `.env` :**
```env
DEBUG=False
```

2. **Générer certificats SSL :**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

3. **Activer Nginx avec SSL :**
```bash
docker-compose --profile production up nginx -d
```

4. **Modifier settings.py :**
```python
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
```

### 🌍 **Accès Application**

Une fois démarré, accédez à :
- **Interface principale (dev)** : http://localhost:8000
- **Interface principale (prod)** : http://localhost:8150  
- **Administration (dev)** : http://localhost:8000/admin
- **Administration (prod)** : http://localhost:8150/admin
- **Comptes par défaut** : admin / admin123 (mode dev)

L'application fonctionne maintenant parfaitement en HTTP ! 🎯