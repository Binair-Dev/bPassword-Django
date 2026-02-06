// DOM Elements
const apiUrlInput = document.getElementById('api-url');
const apiKeyInput = document.getElementById('api-key');
const testConnectionBtn = document.getElementById('test-connection');
const saveConfigBtn = document.getElementById('save-config');
const testResult = document.getElementById('test-result');
const extensionVersionSpan = document.getElementById('extension-version');
const infoVersionSpan = document.getElementById('info-version');
const toast = document.getElementById('toast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadConfiguration();
  setupEventListeners();
});

function setupEventListeners() {
  testConnectionBtn.addEventListener('click', testConnection);
  saveConfigBtn.addEventListener('click', saveConfiguration);
}

// Load configuration from storage
async function loadConfiguration() {
  try {
    const result = await chrome.storage.local.get(['apiUrl', 'apiKey']);

    if (result.apiUrl) {
      apiUrlInput.value = result.apiUrl;
    }

    if (result.apiKey) {
      apiKeyInput.value = result.apiKey;
    }

    // Load extension version
    const manifest = chrome.runtime.getManifest();
    extensionVersionSpan.textContent = manifest.version;
    infoVersionSpan.textContent = manifest.version;
  } catch (error) {
    console.error('Error loading configuration:', error);
    showTestResult('error', 'Erreur lors du chargement de la configuration');
  }
}

// Save configuration
async function saveConfiguration() {
  try {
    const apiUrl = apiUrlInput.value.trim();
    const apiKey = apiKeyInput.value.trim();

    // Validate API URL
    if (!apiUrl) {
      showTestResult('error', 'L\'URL de l\'API est requise');
      return;
    }

    // Validate API Key (64 hex characters)
    if (!apiKey) {
      showTestResult('error', 'La clé API est requise');
      return;
    }

    if (!/^[a-f0-9]{64}$/i.test(apiKey)) {
      showTestResult('error', 'La clé API doit contenir 64 caractères hexadécimaux');
      return;
    }

    // Save to storage
    await chrome.storage.local.set({ apiUrl, apiKey });

    showTestResult('success', 'Configuration enregistrée avec succès !');
    showToast('Configuration enregistrée');

    // Notify background script
    chrome.runtime.sendMessage({ action: 'updateBadge', connected: true });
  } catch (error) {
    console.error('Error saving configuration:', error);
    showTestResult('error', `Erreur lors de l'enregistrement: ${error.message}`);
  }
}

// Test connection
async function testConnection() {
  const apiUrl = apiUrlInput.value.trim();
  const apiKey = apiKeyInput.value.trim();

  // Validate inputs
  if (!apiUrl) {
    showTestResult('error', 'Veuillez entrer l\'URL de l\'API');
    return;
  }

  if (!apiKey) {
    showTestResult('error', 'Veuillez entrer la clé API');
    return;
  }

  if (!/^[a-f0-9]{64}$/i.test(apiKey)) {
    showTestResult('error', 'La clé API doit contenir 64 caractères hexadécimaux');
    return;
  }

  showTestResult('info', 'Test de connexion en cours...');

  try {
    // Temporarily update API instance
    await api.setApiKey(apiKey);

    // Test connection
    const result = await api.testConnection();

    if (result.success) {
      showTestResult('success', 'Connexion réussie ! 🎉');
      showToast('Connexion réussie');
      chrome.runtime.sendMessage({ action: 'updateBadge', connected: true });
    } else {
      showTestResult('error', `Échec de la connexion: ${result.message}`);
      chrome.runtime.sendMessage({ action: 'updateBadge', connected: false });
    }
  } catch (error) {
    console.error('Connection test error:', error);
    showTestResult('error', `Erreur de connexion: ${error.message}`);
    chrome.runtime.sendMessage({ action: 'updateBadge', connected: false });
  }
}

// Show test result
function showTestResult(type, message) {
  testResult.className = `test-result ${type}`;
  testResult.textContent = message;

  if (type === 'success') {
    testResult.style.borderColor = 'var(--success-color)';
    testResult.style.color = 'var(--success-color)';
  } else if (type === 'error') {
    testResult.style.borderColor = 'var(--danger-color)';
    testResult.style.color = 'var(--danger-color)';
  } else {
    testResult.style.borderColor = 'var(--border-color)';
    testResult.style.color = 'var(--text-color)';
  }
}

// Show toast notification
function showToast(message) {
  toast.textContent = message;
  toast.classList.remove('hidden');

  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3000);
}
