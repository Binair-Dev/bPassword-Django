# ☁️ Build APK Cloud (SANS installer Android Studio)

## 🎯 Le plus simple possible - 3 commandes !

### Prérequis (juste ça !)
```bash
# 1. Node.js (tu as déjà probablement)
node --version

# 2. Git (tu as déjà)
```

---

## 🚀 3 Commandes, c'est tout !

### Commande 1 : Installe EAS CLI
```bash
npm install -g eas-cli
```

*(Une seule fois, takes ~30s)*

### Commande 2 : Login
```bash
eas login
```

1. Ça ouvre un navigateur
2. Crée un compte Expo (gratuit)
3. Connecte-toi avec GitHub/Google
4. Retourne au terminal

### Commande 3 : Build !
```bash
cd bPassword-Django/bpassword-mobile
eas build:configure
eas build --platform android --profile apk
```

**C'est tout !** Expo compile l'APK sur leurs serveurs et t'envoie le lien par email.

---

## 📥 Récupérer ton APK

Une fois le build terminé (5-10 minutes) :

**Option A : Dans le terminal**
Tu verras un lien de téléchargement direct.

**Option B : Par email**
Expo t'envoie un lien à ton adresse email.

**Option C : Sur le dashboard**
1. Va sur https://expo.dev/
2. Connecte-toi
3. Clique sur ton projet "bpassword-mobile"
4. Télécharge l'APK

---

## ⚠️ Premier build seulement

La **première fois**, il te demandera de configurer le projet :

```
Would you like to create a project on Expo.io? (Y/n)
```
Réponds `Y` (ou appuie sur Enter)

```
? Would you like to use an existing account?
```
Choisis ton compte (GitHub/Google)

C'est tout ! Les prochains builds seront encore plus rapides.

---

## 🎉 C'est fini !

1. Télécharge l'APK
2. Envoie-le à ton téléphone (email, cloud, USB)
3. Installe et c'est parti !

**Avantages :**
- ✅ Aucune installation sur ton PC
- ✅ Pas d'Android Studio
- ✅ Pas de Java JDK
- ✅ Pas de configuration SDK
- ✅ Build cloud automatique
- ✅ Gratuit pour les builds dev

**Inconvénients :**
- Premier build prend 5-10 min
- Besoin d'une connexion internet

---

## 📱 Pour les builds suivants

Une fois configuré, c'est juste :

```bash
cd bPassword-Django/bpassword-mobile
eas build --platform android --profile apk
```

Et tu récupères ton APK en quelques minutes ! 🚀
