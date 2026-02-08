# 📱 Build APK Local - Guide Complet

## 🛠️ Prérequis

### 1. Android Studio (Obligatoire)
```
Télécharge : https://developer.android.com/studio
Installe et lance une fois pour télécharger le SDK
```

### 2. Java JDK 17+
```bash
# Vérifie ta version Java
java -version

# Si pas installé ou < 17 :
# Windows : https://adoptium.net/
# Mac : brew install openjdk@17
# Linux : sudo apt install openjdk-17-jdk
```

### 3. Variables d'environnement

**Windows (Powershell) :**
```powershell
# Ajoute à tes variables système :
ANDROID_HOME = C:\Users\TonUser\AppData\Local\Android\Sdk

# Ajoute au PATH :
C:\Users\TonUser\AppData\Local\Android\Sdk\platform-tools
C:\Users\TonUser\AppData\Local\Android\Sdk\cmdline-tools\latest\bin
```

**Linux/Mac (ajoute à ~/.bashrc ou ~/.zshrc) :**
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/emulator
```

**Redémarre ton terminal après !**

---

## 🚀 Étape par Étape

### 1. Clone le repo
```bash
git clone https://github.com/Binair-Dev/bPassword-Django.git
cd bPassword-Django/bpassword-mobile
```

### 2. Installe les dépendances
```bash
npm install
```

*(Cela peut prendre quelques minutes)*

### 3. Prépare le projet Android
```bash
npx expo prebuild --platform android
```

Cette commande crée le dossier `android/` avec tout ce qu'il faut.

### 4. Vérifie que le SDK est ok
```bash
cd android
./gradlew --version
```

Tu devrais voir la version de Gradle et Java.

### 5. Build l'APK Debug (Test)
```bash
./gradlew assembleDebug
```

L'APK sera dans : `android/app/build/outputs/apk/debug/app-debug.apk`

### 6. Build l'APK Release (Production)

#### 6a. Crée une clé de signature (une seule fois)
```bash
keytool -genkey -v -keystore bpassword.keystore -alias bpassword -keyalg RSA -keysize 2048 -validity 10000
```

Réponds aux questions :
- **Mot de passe du keystore** (souviens-toi-en !)
- **Prénom, nom, organisation, ville, pays**
- **Mot de passe de la clé** (même que le keystore ou différent)

#### 6b. Place le keystore au bon endroit
```bash
# Le keystore a été créé dans le dossier courant
# Copie-le ou déplace-le dans android/app/
mv bpassword.keystore app/
```

#### 6c. Configure Gradle avec le keystore
```bash
# Crée ou édite android/gradle.properties
nano gradle.properties
```

Ajoute ces lignes (remplace avec tes mots de passe) :
```properties
MYAPP_UPLOAD_STORE_FILE=bpassword.keystore
MYAPP_UPLOAD_KEY_ALIAS=bpassword
MYAPP_UPLOAD_STORE_PASSWORD=TON_MOT_DE_PASSE
MYAPP_UPLOAD_KEY_PASSWORD=TON_MOT_DE_PASSE
```

#### 6d. Build le release APK
```bash
./gradlew assembleRelease
```

**L'APK signé sera dans :**
```
android/app/build/outputs/apk/release/app-release.apk
```

---

## 📤 Installer l'APK sur ton téléphone

### Via ADB (si connecté en USB)
```bash
adb install android/app/build/outputs/apk/release/app-release.apk
```

### Via le téléphone
1. Envoie l'APK à ton téléphone (email, cloud, USB)
2. Clique sur le fichier
3. Autorise l'installation d'apps inconnues
4. Install !

---

## 🔧 Problèmes Fréquents

### "gradlew: command not found"
```bash
chmod +x android/gradlew
```

### "SDK location not found"
Configure `ANDROID_HOME` correctement (voir Prérequis)

### "Out of memory"
```bash
# Dans android/gradle.properties, ajoute :
org.gradle.jvmargs=-Xmx2048m
```

### Build très lent
```bash
./gradlew assembleRelease --no-daemon
```

### Erreur de signature
Vérifie que tes mots de passe dans `gradle.properties` sont corrects.

---

## 🎉 Tu as ton APK !

```
bpassword-mobile/
└── android/
    └── app/
        └── build/
            └── outputs/
                └── apk/
                    └── release/
                        └── app-release.apk  ← C'est ton fichier !
```

Installe-le, entre ta clé API, et c'est parti ! 🔐
