// State
let credentials = [];
let searchTimeout = null;
let currentEditingId = null;

// DOM Elements
const credentialsList = document.getElementById('credentials-list');
const searchInput = document.getElementById('search-input');
const addCredentialBtn = document.getElementById('add-credential-btn');
const settingsBtn = document.getElementById('settings-btn');
const modal = document.getElementById('credential-modal');
const modalTitle = document.getElementById('modal-title');
const credentialForm = document.getElementById('credential-form');
const credentialIdInput = document.getElementById('credential-id');
const nameInput = document.getElementById('name');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const togglePasswordBtn = document.getElementById('toggle-password');
const generatePasswordBtn = document.getElementById('generate-password');
const cancelBtn = document.getElementById('cancel-btn');
const connectionStatus = document.getElementById('connection-status');
const toast = document.getElementById('toast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadCredentials();
  updateConnectionStatus();
  setupEventListeners();
});

function setupEventListeners() {
  searchInput.addEventListener('input', debounce(handleSearch, 300));
  addCredentialBtn.addEventListener('click', () => openModal());
  settingsBtn.addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });
  cancelBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
  credentialForm.addEventListener('submit', handleSubmit);
  togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
  generatePasswordBtn.addEventListener('click', generatePassword);

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'n' && e.ctrlKey) {
      e.preventDefault();
      openModal();
    }
  });
}

// Load credentials
async function loadCredentials() {
  try {
    const result = await api.listCredentials();
    credentials = result;
    renderCredentials();
    updateConnectionStatus(true);
  } catch (error) {
    console.error('Error loading credentials:', error);
    showError(error.message);
    updateConnectionStatus(false);
  }
}

// Render credentials list
function renderCredentials(filteredCredentials = null) {
  const credentialsToRender = filteredCredentials || credentials;

  if (credentialsToRender.length === 0) {
    credentialsList.innerHTML = `
      <div class="empty-state">
        <p>${searchInput.value ? 'Aucun identifiant trouvé' : 'Aucun identifiant enregistré'}</p>
        <p style="font-size: 12px; margin-top: 8px;">Cliquez sur "Ajouter" pour créer le premier</p>
      </div>
    `;
    return;
  }

  credentialsList.innerHTML = credentialsToRender.map(cred => `
    <div class="credential-card" data-id="${cred.id}">
      <div class="credential-info">
        <div class="credential-name">${escapeHtml(cred.name)}</div>
        <div class="credential-username">${escapeHtml(cred.username)}</div>
      </div>
      <div class="credential-actions">
        <button class="copy-btn copy-username" data-credential-id="${cred.id}" data-type="username" title="Copier l'utilisateur">
          <span>👤</span> Copier user
        </button>
        <button class="copy-btn copy-password" data-credential-id="${cred.id}" data-type="password" title="Copier le mot de passe">
          <span>🔑</span> Copier mdp
        </button>
        <button class="copy-btn edit-btn" data-credential-id="${cred.id}" data-type="edit" title="Modifier">
          <span>✏️</span>
        </button>
        <button class="copy-btn delete-btn" data-credential-id="${cred.id}" data-type="delete" title="Supprimer">
          <span>🗑️</span>
        </button>
      </div>
    </div>
  `).join('');

  // Add event listeners to credential cards
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      handleCredentialAction(btn);
    });
  });

  document.querySelectorAll('.credential-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = parseInt(card.dataset.id);
      editCredential(id);
    });
  });
}

// Handle credential actions
async function handleCredentialAction(btn) {
  const credentialId = parseInt(btn.dataset.credentialId);
  const type = btn.dataset.type;

  if (type === 'delete') {
    const confirmed = confirm('Êtes-vous sûr de vouloir supprimer cet identifiant ?');
    if (confirmed) {
      await deleteCredential(credentialId);
    }
    return;
  }

  if (type === 'edit') {
    editCredential(credentialId);
    return;
  }

  // Copy username or password
  const credential = credentials.find(c => c.id === credentialId);
  if (!credential) return;

  const textToCopy = type === 'username' ? credential.username : credential.password;

  try {
    await navigator.clipboard.writeText(textToCopy);
    showSuccess(`${type === 'username' ? 'Nom d\'utilisateur' : 'Mot de passe'} copié !`);

    // Visual feedback
    const card = btn.closest('.credential-card');
    card.classList.add('copied');
    setTimeout(() => card.classList.remove('copied'), 1000);
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    showError('Erreur lors de la copie');
  }
}

// Search with debounce
function handleSearch() {
  const query = searchInput.value.trim().toLowerCase();

  if (!query) {
    renderCredentials(credentials);
    return;
  }

  const filtered = credentials.filter(cred =>
    cred.name.toLowerCase().includes(query) ||
    cred.username.toLowerCase().includes(query)
  );

  renderCredentials(filtered);
}

function debounce(func, wait) {
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(searchTimeout);
      func(...args);
    };
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(later, wait);
  };
}

// Open modal for creating/editing
function openModal(credential = null) {
  currentEditingId = credential ? credential.id : null;
  modalTitle.textContent = credential ? 'Modifier l\'identifiant' : 'Ajouter un identifiant';
  credentialIdInput.value = credential ? credential.id : '';
  nameInput.value = credential ? credential.name : '';
  usernameInput.value = credential ? credential.username : '';
  passwordInput.value = credential ? credential.password : '';

  modal.classList.remove('hidden');
  nameInput.focus();
}

function closeModal() {
  modal.classList.add('hidden');
  credentialForm.reset();
  currentEditingId = null;
}

// Edit credential
async function editCredential(id) {
  const credential = credentials.find(c => c.id === id);
  if (credential) {
    openModal(credential);
  }
}

// Handle form submit
async function handleSubmit(e) {
  e.preventDefault();

  const data = {
    name: nameInput.value.trim(),
    username: usernameInput.value.trim(),
    password: passwordInput.value
  };

  try {
    if (currentEditingId) {
      await api.updateCredential(currentEditingId, data);
      showSuccess('Identifiant modifié avec succès !');
    } else {
      await api.createCredential(data);
      showSuccess('Identifiant créé avec succès !');
    }

    closeModal();
    await loadCredentials();
  } catch (error) {
    console.error('Error saving credential:', error);
    showError(error.message);
  }
}

// Delete credential
async function deleteCredential(id) {
  try {
    await api.deleteCredential(id);
    showSuccess('Identifiant supprimé avec succès !');
    await loadCredentials();
  } catch (error) {
    console.error('Error deleting credential:', error);
    showError(error.message);
  }
}

// Toggle password visibility
function togglePasswordVisibility() {
  const type = passwordInput.type === 'password' ? 'text' : 'password';
  passwordInput.type = type;
  togglePasswordBtn.textContent = type === 'password' ? '👁' : '👁️‍🗨️';
}

// Generate password
function generatePassword() {
  const length = 16;
  const chars = {
    uppercase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    lowercase: 'abcdefghijklmnopqrstuvwxyz',
    numbers: '0123456789',
    symbols: '!@#$%^&*()_+-=[]{}|;:,.<>?'
  };

  let charset = '';
  let password = '';

  // Ensure at least one of each type
  password += chars.uppercase[Math.floor(Math.random() * chars.uppercase.length)];
  password += chars.lowercase[Math.floor(Math.random() * chars.lowercase.length)];
  password += chars.numbers[Math.floor(Math.random() * chars.numbers.length)];
  password += chars.symbols[Math.floor(Math.random() * chars.symbols.length)];

  // Fill the rest
  charset = chars.uppercase + chars.lowercase + chars.numbers + chars.symbols;
  for (let i = password.length; i < length; i++) {
    password += charset[Math.floor(Math.random() * charset.length)];
  }

  // Shuffle the password
  password = password.split('').sort(() => Math.random() - 0.5).join('');

  passwordInput.value = password;
  passwordInput.type = 'text';
  togglePasswordBtn.textContent = '👁️‍🗨️';

  showSuccess('Mot de passe généré !');
}

// Update connection status
function updateConnectionStatus(connected = null) {
  if (connected === true) {
    connectionStatus.textContent = 'Connecté';
    connectionStatus.className = 'status-connected';
  } else if (connected === false) {
    connectionStatus.textContent = 'Non connecté';
    connectionStatus.className = 'status-disconnected';
  } else {
    connectionStatus.textContent = 'Checking...';
    connectionStatus.className = 'status-disconnected';
  }
}

// Show toast notification
function showToast(message, type = 'success') {
  toast.textContent = message;
  toast.style.background = type === 'success' ? 'var(--success-color)' : 'var(--error-color)';
  toast.classList.remove('hidden');

  setTimeout(() => {
    toast.classList.add('hidden');
  }, 3000);
}

function showSuccess(message) {
  showToast(message, 'success');
}

function showError(message) {
  showToast(message, 'error');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
