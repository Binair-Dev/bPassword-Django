# bPassword Mobile

Application mobile pour bPassword - Gestionnaire de mots de passe

## 📱 Fonctionnalités

- ✅ Connexion par clé API (même système que l'extension)
- ✅ Liste des mots de passe avec recherche
- ✅ Copier username / mot de passe en un clic
- ✅ Créer / Modifier / Supprimer des credentials
- ✅ Générateur de mot de passe intégré
- ✅ Stockage sécurisé de la clé API (Keychain/Android Keystore)

## 🚀 Installation et Build

### Prérequis

- Node.js (v18+)
- npm ou yarn
- Android SDK (pour build Android)
- Java JDK 17+

### Étape 1 : Installation des dépendances

```bash
cd bpassword-mobile
npm install
```

### Étape 2 : Configuration des assets (icônes)

Crée les fichiers d'icônes dans le dossier `assets/` :
- `icon.png` (1024x1024) - Icône principale
- `splash.png` (1242x1242) - Écran de démarrage
- `adaptive-icon.png` (1024x1024) - Icône Android adaptive
- `favicon.png` (512x512) - Favicon web

Tu peux utiliser ce générateur d'icônes : https://icon.kitchen/

### Étape 3 : Prébuild (génération du projet natif)

```bash
npx expo prebuild --platform android
```

Cette commande crée le dossier `android/` avec le projet Gradle.

### Étape 4 : Build de l'APK

#### Option A : Build local (debug)

```bash
cd android
./gradlew assembleDebug
```

L'APK sera dans : `android/app/build/outputs/apk/debug/app-debug.apk`

#### Option B : Build release (pour publication)

1. Crée un keystore de signature :

```bash
keytool -genkey -v -keystore bpassword.keystore -alias bpassword -keyalg RSA -keysize 2048 -validity 10000
```

2. Place le fichier `bpassword.keystore` dans `android/app/`

3. Crée le fichier `android/gradle.properties` (ou modifie) :

```properties
MYAPP_UPLOAD_STORE_FILE=bpassword.keystore
MYAPP_UPLOAD_KEY_ALIAS=bpassword
MYAPP_UPLOAD_STORE_PASSWORD=ton_mot_de_passe
MYAPP_UPLOAD_KEY_PASSWORD=ton_mot_de_passe
```

4. Build la release :

```bash
cd android
./gradlew assembleRelease
```

L'APK signé sera dans : `android/app/build/outputs/apk/release/app-release.apk`

## 🧪 Développement

### Lancer en mode développement

```bash
npm start
```

Puis appuie sur :
- `a` pour Android
- `i` pour iOS (Mac uniquement)
- `w` pour Web

### Scanner avec Expo Go

Télécharge l'app **Expo Go** sur ton téléphone, scanne le QR code.

## 📁 Structure du projet

```
bpassword-mobile/
├── App.js                    # Point d'entrée
├── package.json              # Dépendances
├── app.json                  # Configuration Expo
├── assets/                   # Images et icônes
├── src/
│   ├── api/
│   │   └── BPasswordAPI.js   # Classe API (identique à l'extension)
│   ├── screens/
│   │   ├── LoginScreen.js    # Écran de connexion
│   │   ├── CredentialsScreen.js    # Liste des passwords
│   │   └── CredentialDetailScreen.js # Détail/édition
│   └── components/           # Composants réutilisables
```

## 🔌 API Utilisée

L'app utilise exactement la même API que l'extension Chrome :

- Base URL : `https://bpassword.b-services.be/api/`
- Auth : Header `Authorization: Api-Key {64-char-hex}`
- Endpoints :
  - `GET /credentials/` - Liste
  - `POST /credentials` - Créer
  - `PUT /credentials/{id}/` - Modifier
  - `DELETE /credentials/{id}` - Supprimer

## 🔒 Sécurité

- La clé API est stockée dans le **Keychain** (iOS) ou **Android Keystore**
- Pas de session web, pas de 2FA à chaque fois
- Connexion persistante tant que la clé API est valide

## 🐛 Troubleshooting

### Erreur "gradlew not found"

```bash
chmod +x android/gradlew
```

### Erreur de signature

Vérifie que ton keystore est correctement configuré dans `gradle.properties`.

### Build échoue avec erreur de mémoire

```bash
cd android
./gradlew assembleRelease --no-daemon
```

### Reset du projet

```bash
rm -rf android ios
npx expo prebuild --platform android
```

## 📦 Distribution

### Partager l'APK

Une fois le build terminé, tu peux partager `app-release.apk` directement.

### Google Play Store

1. Crée un compte développeur ($25)
2. Build un AAB (Android App Bundle) :

```bash
cd android
./gradlew bundleRelease
```

3. Télécharge `app-release.aab` sur la Console Play Store.

---

**Note** : Cette app ne remplace pas l'extension navigateur, c'est un complément pour mobile ! 🔐
