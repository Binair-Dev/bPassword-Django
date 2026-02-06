# bPassword Extension - Quick Setup Guide

## Overview

This guide will help you set up and test the bPassword Chrome/Brave extension.

## Prerequisites

- Docker and Docker Compose installed
- Chrome or Brave browser
- bPassword Django server running

## Step 1: Configure CORS on Server (Already Done)

The server has been configured with CORS support:

✅ `django-cors-headers` added to `requirements.txt`
✅ `corsheaders` added to `INSTALLED_APPS` in `settings.py`
✅ `CorsMiddleware` added to `MIDDLEWARE` in `settings.py`
✅ CORS settings configured in `settings.py`

## Step 2: Rebuild and Start the Docker Container

Since we modified the requirements and settings, rebuild the container:

```bash
# Stop any running containers
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

## Step 3: Verify the Server is Running

```bash
# Check if the container is running
docker-compose ps

# Check logs for any errors
docker-compose logs -f app

# Test the API is responding
curl https://bpassword.b-services.be/api/credentials/
```

## Step 4: Install the Extension in Chrome/Brave

### For Chrome:
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `bpassword-extension` folder
5. The extension should now appear in your extensions list

### For Brave:
1. Open Brave and navigate to `brave://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `bpassword-extension` folder

## Step 5: Configure the Extension

1. Click on the bPassword icon in your browser toolbar
2. Click on "⚙️ Paramètres" (Settings)
3. Enter the API URL: `https://bpassword.b-services.be/api`
4. Enter your API Key (64 hex characters)
   - To get an API key, log in to bPassword and navigate to the API keys section
5. Click "Tester la connexion" (Test connection)
6. If successful, you'll see a green success message
7. Click "Enregistrer" (Save)

## Step 6: Test the Extension

### Test 1: View Credentials
1. Click the bPassword icon
2. You should see a list of your credentials
3. The connection status should show "Connecté" (green)

### Test 2: Search
1. Type in the search box
2. The list should filter in real-time
3. Press Escape to clear search

### Test 3: Copy Username
1. Click "👤 Copier" button next to a credential
2. Paste into a text editor - should be the username

### Test 4: Copy Password
1. Click "🔑 Copier" button next to a credential
2. Paste into a text editor - should be the password

### Test 5: Create Credential
1. Click "+ Ajouter"
2. Fill in the form:
   - Name: Test Credential
   - Username: testuser
   - Click "🎲" to generate a password
3. Click "Enregistrer"
4. The new credential should appear in the list

### Test 6: Edit Credential
1. Click on a credential or the "✏️" button
2. Modify the name or password
3. Click "Enregistrer"
4. Changes should be reflected

### Test 7: Delete Credential
1. Click the "🗑️" button on a credential
2. Confirm the deletion
3. The credential should be removed

### Test 8: Content Script Injection
1. Navigate to a login page (e.g., github.com/login)
2. Look for the password field
3. You should see a "🔑" button injected next to it
4. Click the button - should open the bPassword popup

## Troubleshooting

### Connection Test Fails
- Verify the API URL is correct (should end with `/api`)
- Check your API key is exactly 64 hex characters
- Verify the server is running and accessible
- Check browser console for errors (F12 → Console)

### Extension Doesn't Appear
- Make sure Developer mode is enabled
- Verify you selected the correct folder (`bpassword-extension`)
- Check for errors in the extensions page

### Content Script Not Injecting
- Refresh the page after installing the extension
- Check that the page has a password field (`<input type="password">`)
- Check browser console for JavaScript errors

### CORS Errors in Console
- Verify django-cors-headers is installed on the server
- Check that `CORS_ALLOW_ALL_ORIGINS = True` is set in settings.py
- Verify the server was rebuilt after adding CORS support
- Check server logs: `docker-compose logs app | grep -i cors`

### Badge Shows Red "!"
- API key may be invalid or not configured
- Click the extension icon and go to Settings
- Re-enter your API key and test connection

### Password Not Copying
- Some sites block clipboard access
- Check browser permissions for clipboard access
- Try using Ctrl+C to manually copy from the opened credential

## Development

### Reload Extension After Changes
1. Go to `chrome://extensions/`
2. Click the refresh (🔄) button on the bPassword extension
3. For content scripts, reload the web page

### Debugging

**Popup:**
- Right-click on the popup → Inspect

**Background Script:**
- chrome://extensions/ → Service worker → Inspect

**Content Script:**
- F12 on a web page → Sources tab → Extensions section

### View Extension Files

The extension is located in the `bpassword-extension/` directory:

```
bpassword-extension/
├── manifest.json              # Extension manifest
├── popup/                     # Popup interface
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   └── api.js
├── options/                   # Settings page
│   ├── options.html
│   ├── options.css
│   ├── options.js
│   └── api.js
├── background/                # Service worker
│   └── background.js
├── content/                   # Content script
│   ├── content.js
│   └── content.css
├── icons/                     # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md                  # Documentation
```

## Production Deployment

### 1. Update API URL
In production, ensure the extension points to your production API:
- `https://bpassword.b-services.be/api`

### 2. Remove Development Code
- Remove any console.log statements
- Remove test/development settings

### 3. Create Distribution Package
```bash
cd bpassword-extension
zip -r bpassword-extension.zip \
  manifest.json \
  popup/ \
  options/ \
  background/ \
  content/ \
  icons/*.png \
  README.md \
  --exclude="icons/node_modules" \
  --exclude="icons/generate-icons.js"
```

### 4. Publish to Chrome Web Store
1. Create a Chrome Web Store Developer account ($5 one-time fee)
2. Prepare screenshots (min: 1280x800 or 640x400)
3. Write detailed description
4. Upload the zip file
5. Submit for review

### 5. Brave Add-ons
Brave uses the Chrome Web Store, so no separate submission is needed.

## Security Considerations

- Always use HTTPS in production
- Protect API keys like passwords
- Enable rate limiting on the server
- Regularly rotate API keys
- Monitor API access logs
- Enable 2FA on the bPassword server

## Next Steps

1. Test the extension thoroughly with real credentials
2. Gather user feedback
3. Consider adding features like:
   - Auto-fill on detected forms
   - Export/Import functionality
   - Password strength indicator
   - Biometric unlock for the extension

## Support

For issues or questions:
- Check the server logs: `docker-compose logs -f`
- Check browser console (F12 → Console)
- Review the extension manifest and settings
- Consult the README.md in the extension folder

---

**Note:** This extension is a Manifest V3 extension, which is the latest standard for Chrome and Brave extensions.
