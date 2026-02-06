# bPassword Extension Chrome/Brave

Extension de navigateur pour gérer vos identifiants bPassword directement depuis Chrome ou Brave.

## Fonctionnalités

- 🔐 **Gestion sécurisée** : Stockage et gestion de vos identifiants via l'API bPassword
- 🔍 **Recherche en temps réel** : Trouvez rapidement vos identifiants
- 📋 **Copie rapide** : Copiez le username et le password en un clic
- ✏️ **CRUD complet** : Créez, éditez et supprimez vos identifiants
- 🎲 **Générateur de mot de passe** : Générez des mots de passe sécurisés
- 🌐 **Injection automatique** : Bouton d'icône sur les formulaires de login
- 🌙 **Mode sombre/clair** : S'adapte automatiquement à vos préférences système
- 🔑 **Clé API sécurisée** : Votre clé API est stockée localement

## Installation

### Installation depuis Chrome/Brave

1. Clonez ou téléchargez ce repository
2. Ouvrez Chrome ou Brave et naviguez vers `chrome://extensions/` (ou `brave://extensions/`)
3. Activez le "Mode développeur" dans le coin supérieur droit
4. Cliquez sur "Charger l'extension non empaquetée" (Load unpacked)
5. Sélectionnez le dossier `bpassword-extension`

### Configuration

1. Cliquez sur l'icône bPassword dans votre barre d'outils
2. Cliquez sur "Paramètres" (⚙️)
3. Entrez l'URL de l'API : `https://bpassword.b-services.be/api`
4. Entrez votre clé API (64 caractères hexadécimaux)
5. Cliquez sur "Tester la connexion"
6. Si la connexion réussit, cliquez sur "Enregistrer"

## Utilisation

### Popup principal

Le popup s'ouvre lorsque vous cliquez sur l'icône bPassword dans votre barre d'outils.

**Fonctionnalités :**
- **Recherche** : Tapez dans la barre de recherche pour filtrer vos identifiants
- **Copie** : Cliquez sur "👤 Copier" pour le username ou "🔑 Copier" pour le password
- **Création** : Cliquez sur "+ Ajouter" pour créer un nouvel identifiant
- **Édition** : Cliquez sur un identifiant ou sur le bouton "✏️" pour le modifier
- **Suppression** : Cliquez sur le bouton "🗑️" pour supprimer un identifiant

### Générateur de mot de passe

Lors de la création ou de l'édition d'un identifiant, utilisez le bouton "🎲" pour générer un mot de passe sécurisé de 16 caractères incluant :
- Lettres majuscules
- Lettres minuscules
- Chiffres
- Caractères spéciaux

### Injection sur formulaires

L'extension détecte automatiquement les champs de mot de passe sur les pages web et injecte un bouton "🔑" à côté.

Pour utiliser :
1. Naviguez vers une page de login
2. Cliquez sur le bouton "🔑" à côté du champ de mot de passe
3. Le popup bPassword s'ouvrira
4. Recherchez et copiez l'identifiant souhaité

## Raccourcis clavier

- `Ctrl + N` : Ouvrir le formulaire de création (dans le popup)
- `Escape` : Fermer le modal de création/édition

## Structure de l'extension

```
bpassword-extension/
├── manifest.json              # Manifeste Manifest V3
├── popup/
│   ├── popup.html            # Interface principale
│   ├── popup.css             # Styles du popup
│   ├── popup.js              # Logique du popup
│   └── api.js                # Service de communication API
├── options/
│   ├── options.html          # Page de paramètres
│   ├── options.css           # Styles des options
│   ├── options.js            # Logique des options
│   └── api.js                # Service de communication API
├── background/
│   └── background.js         # Service worker
├── content/
│   ├── content.js            # Script de contenu
│   └── content.css           # Styles de contenu
├── icons/
│   ├── icon16.png            # Icône 16px
│   ├── icon48.png            # Icône 48px
│   ├── icon128.png           # Icône 128px
│   └── icon.svg              # Source SVG
└── README.md                  # Documentation
```

## Configuration requise

### Serveur

L'extension nécessite un serveur bPassword avec l'API REST activée et CORS configuré.

### CORS

Le serveur doit avoir `django-cors-headers` configuré avec `CORS_ALLOW_ALL_ORIGINS = True` pour permettre l'accès depuis n'importe quel réseau.

### Clé API

Vous devez posséder une clé API valide de 64 caractères hexadécimaux pour utiliser l'extension.

## Sécurité

- 🔒 La clé API est stockée localement dans `chrome.storage.local`
- 🔐 Toutes les communications utilisent HTTPS en production
- 👁 Les mots de passe ne sont jamais stockés en clair dans l'extension
- ✅ Toutes les validations sont effectuées côté serveur
- 🚦 Rate limiting côté serveur pour prévenir les abus
- 🔒 Permissions minimales nécessaires (`storage`, `clipboardWrite`, `activeTab`, `tabs`)

## Développement

### Recharger l'extension

Après avoir modifié le code :
1. Allez sur `chrome://extensions/`
2. Cliquez sur le bouton "Actualiser" (🔄) de l'extension
3. Pour les scripts de contenu, rechargez la page web

### Débogage

- **Popup** : Clic droit sur le popup > Inspecter
- **Background script** : Page d'extensions > "Service worker" > Inspecter
- **Content script** : Inspecter la page web > Onglet Sources > Extensions

### Tester CORS

```bash
curl -H "Origin: chrome-extension://test" \
     -H "Authorization: Api-Key <your_api_key>" \
     -I https://bpassword.b-services.be/api/credentials/
```

Vérifiez que le header `Access-Control-Allow-Origin: *` est présent dans la réponse.

## Publication

### Package pour publication

Pour publier sur le Chrome Web Store ou le Brave Add-ons, créez un fichier zip contenant :

```
bpassword-extension.zip
├── manifest.json
├── popup/
├── options/
├── background/
├── content/
└── icons/
```

**N'incluez pas :**
- Le dossier `node_modules/`
- Les fichiers `.git/`
- Les fichiers de développement (tests, documentation technique)

### Chrome Web Store

1. Créez un compte développeur (frais uniques de $5)
2. Préparez des captures d'écran (min: 1280x800 ou 640x400)
3. Rédigez une description détaillée
4. Uploadez le package zip
5. Soumettez pour révision

### Brave Add-ons

Brave utilise le Chrome Web Store pour les extensions. Une fois publiée sur Chrome, elle sera disponible pour Brave.

## FAQ

**Q: L'extension fonctionne-t-elle hors ligne ?**
R: Non, l'extension nécessite une connexion internet pour communiquer avec l'API bPassword.

**Q: Puis-je utiliser plusieurs instances de bPassword ?**
R: Oui, en configurant différentes URLs API dans les paramètres.

**Q: Mes mots de passe sont-ils stockés dans le navigateur ?**
R: Non, les mots de passe ne sont jamais stockés en clair dans le navigateur. Ils sont toujours récupérés depuis le serveur sécurisé.

**Q: Comment savoir si l'extension est connectée ?**
R: Le badge de l'extension affiche :
- Vert : Connecté (pas de texte)
- Rouge : Non connecté (texte "!")

**Q: L'extension collecte-t-elle des données ?**
R: Non, l'extension ne collecte aucune donnée personnelle ou de navigation. Elle communique uniquement avec votre serveur bPassword.

**Q: Comment générer une nouvelle clé API ?**
R: Connectez-vous à votre interface bPassword et générez une nouvelle clé API depuis les paramètres de votre compte.

## Support

Pour tout problème ou question :

- 📧 Email : [votre email]
- 🐛 Issues : [GitHub Issues]
- 📖 Documentation : [Documentation serveur]

## Licence

[Votre licence]

## Remerciements

- bPassword team
- Chrome/Brave extension documentation
- Django REST Framework

---

**Note de sécurité** : Assurez-vous toujours d'utiliser HTTPS en production et de protéger votre clé API comme n'importe quel mot de passe.
