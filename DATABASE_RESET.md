# 🧹 Nettoyage Base de Données - bPassword Django

## 🎯 Objectif

Nettoyer complètement la base de données bPassword pour repartir sur une base vierge :
- Supprimer tous les utilisateurs (`auth_user`)
- Supprimer tous les identifiants (`passwords_credentials`)
- Recréer un superutilisateur propre

## 🚀 **Méthodes de Nettoyage**

### 1. **Méthode Docker (Recommandée)**

#### Via le script intégré
```bash
# Nettoie la base de données du conteneur en cours
./docker-start.sh reset-db
```

#### Ou directement
```bash
# Exécute le script de nettoyage Docker
./scripts/reset_db_docker.sh
```

**Fonctionnalités :**
- ✅ Détection automatique du conteneur actif
- ✅ Suppression sécurisée avec confirmation
- ✅ Création optionnelle d'un nouveau superutilisateur
- ✅ Support tous les modes (simple/dev/prod)

### 2. **Méthode Locale (Environment Python)**

```bash
# Depuis l'environnement virtuel local
source venv/bin/activate
cd bpassword
python ../reset_database.py
```

**Avantages :**
- ✅ Fonctionne sans Docker
- ✅ Interaction directe avec Django
- ✅ Script Python détaillé

## 🔧 **Processus de Nettoyage**

### Étapes automatiques :
1. **Comptage** des données existantes
2. **Confirmation** de l'utilisateur (sécurité)
3. **Suppression** de `passwords_credentials`
4. **Suppression** de `auth_user`
5. **Base vide** - aucun utilisateur créé

### Données supprimées :
- 🗑️ **Tous les identifiants sauvegardés**
- 🗑️ **Tous les comptes utilisateurs**
- 🗑️ **Historique de connexions**

### Données préservées :
- ✅ **Structure des tables** (migrations)
- ✅ **Configuration Django**
- ✅ **Fichiers de l'application**

### Résultat final :
- 🔒 **Base de données COMPLÈTEMENT VIDE**
- 👤 **Aucun utilisateur créé automatiquement**
- 📝 **Inscription requise** pour créer des comptes

## ⚠️ **Sécurité**

### Confirmations multiples :
- ❓ "Voulez-vous vraiment supprimer TOUTES les données ?"
- ❓ "Créer un nouveau superutilisateur ?"

### Action irréversible :
- 🚨 **IMPOSSIBLE d'annuler** après confirmation
- 💾 **AUCUNE sauvegarde automatique**
- 🗑️ **PERTE DÉFINITIVE** des données

## 👤 **Après Nettoyage**

**Aucun utilisateur créé automatiquement !**
- 🔒 Base de données complètement vide
- 📝 Utilisation de l'interface d'inscription obligatoire
- 🆕 Création manuelle des premiers comptes

**Accès après nettoyage :**
- 🌐 Interface: http://localhost:8150 (ou votre IP)
- 📝 Page d'inscription: http://localhost:8150/accounts/register/
- 🔑 Créez votre premier compte via l'interface

## 🔍 **Vérifications**

### Vérifier le nettoyage :
```bash
# Via Docker
docker-compose -f docker-compose.simple.yml exec web python -c "
from django.contrib.auth.models import User
from passwords.models import Credentials
print(f'Utilisateurs: {User.objects.count()}')
print(f'Identifiants: {Credentials.objects.count()}')
"

# Accès web
curl -I http://localhost:8150/admin
```

### Logs de nettoyage :
```bash
# Voir les logs du conteneur
docker-compose -f docker-compose.simple.yml logs web
```

## 📋 **Cas d'Usage**

### Quand nettoyer la base ?
- ✅ **Développement** : reset fréquent pour tests
- ✅ **Démonstration** : données propres pour démo
- ✅ **Migration** : changement de structure
- ✅ **Débogage** : éliminer données corrompues

### Alternatives au nettoyage :
- 🔄 **Sauvegarde/Restauration** : `./docker-start.sh backup`
- 📤 **Export/Import** : boutons dans l'interface
- 🗃️ **Nouveau volume** : `docker-compose down -v`

## ✅ **Résultat Final**

Après nettoyage réussi :
- 🔐 Base de données complètement vierge
- 👤 Aucun utilisateur dans la base
- 📝 Interface d'inscription disponible
- 📊 0 identifiants stockés
- 👥 0 utilisateur - base totalement vide

**La base de données est maintenant propre et prête à l'emploi !** 🎯