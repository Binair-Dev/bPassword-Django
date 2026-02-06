// Content script for injecting bPassword buttons on login forms

// Track if we've already scanned
let hasScanned = false;

// DOM Observer for dynamic content
const observer = new MutationObserver(debounce((mutations) => {
  detectLoginFields();
}, 500));

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  scanPage();
});

// Also run in case DOMContentLoaded already fired
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  scanPage();
}

// Start observing DOM changes
observer.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: false,
  characterData: false
});

// Scan the entire page for login fields
function scanPage() {
  if (hasScanned) return;
  detectLoginFields();
  hasScanned = true;
}

// Detect login fields on the page
function detectLoginFields() {
  const passwordInputs = document.querySelectorAll('input[type="password"]');

  passwordInputs.forEach(input => {
    // Skip if we've already injected a button
    if (input.dataset.bPasswordInjected) return;

    // Skip if input is hidden or has no parent
    if (!input.offsetParent || input.type === 'hidden') return;

    // Find the parent element to inject the button
    const parent = findInjectableParent(input);
    if (parent) {
      injectButton(input, parent);
      input.dataset.bPasswordInjected = 'true';
    }
  });
}

// Find the best parent element to inject the button
function findInjectableParent(input) {
  // Check if input is in a form
  const form = input.closest('form');
  if (form) {
    // Check for input wrapper or container
    const wrapper = input.parentElement;
    if (wrapper && (wrapper.classList.contains('form-group') ||
                     wrapper.classList.contains('input-group') ||
                     wrapper.classList.contains('field'))) {
      return wrapper;
    }
    // Check for label + input wrapper
    const label = input.previousElementSibling;
    if (label && (label.tagName === 'LABEL' ||
                  (label.className && label.className.includes('label')))) {
      return input.parentElement;
    }
  }

  // Default to parent element
  return input.parentElement;
}

// Inject bPassword button next to password field
function injectButton(passwordInput, parent) {
  // Check if parent has position: relative
  const computedStyle = window.getComputedStyle(parent);
  if (computedStyle.position === 'static') {
    parent.style.position = 'relative';
  }

  // Create button container
  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'bpassword-button-container';
  buttonContainer.style.cssText = `
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 4px;
    z-index: 9999;
  `;

  // Create the bPassword button
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'bpassword-inject-btn';
  button.innerHTML = '🔑';
  button.title = 'Chercher dans bPassword';
  button.setAttribute('aria-label', 'Chercher dans bPassword');

  button.style.cssText = `
    background: #4CAF50;
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    font-size: 16px;
    padding: 6px 8px;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  // Add hover effect
  button.addEventListener('mouseenter', () => {
    button.style.background = '#45a049';
  });
  button.addEventListener('mouseleave', () => {
    button.style.background = '#4CAF50';
  });

  // Handle button click
  button.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Just show a notification, don't send message to avoid redirect loop
    showNotification();
  });

  // Add button to container
  buttonContainer.appendChild(button);

  // Add container to parent
  parent.appendChild(buttonContainer);

  // Adjust input padding to make room for button
  const inputPaddingRight = parseInt(window.getComputedStyle(passwordInput).paddingRight) || 0;
  passwordInput.style.paddingRight = `${inputPaddingRight + 50}px`;
}

// Open password manager popup
function openPasswordManager() {
  // Send message to extension to open popup
  chrome.runtime.sendMessage({
    action: 'openPopup',
    url: window.location.href
  }).catch(() => {
    // If extension is not available, show notification
    showNotification();
  });
}

// Show notification that bPassword extension is available
function showNotification() {
  const notification = document.createElement('div');
  notification.className = 'bpassword-notification';
  notification.innerHTML = `
    <div class="bpassword-notification-content">
      <span>🔑</span>
      <span>Cliquez sur l'icône bPassword dans votre barre d'outils</span>
      <button class="bpassword-close-btn">×</button>
    </div>
  `;

  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 16px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    animation: slideIn 0.3s ease;
  `;

  // Add animation styles
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateX(100%);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
  `;
  document.head.appendChild(style);

  document.body.appendChild(notification);

  // Close button handler
  const closeBtn = notification.querySelector('.bpassword-close-btn');
  closeBtn.style.cssText = `
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    margin-left: 12px;
  `;

  closeBtn.addEventListener('click', () => {
    notification.remove();
  });

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Debounce function to prevent excessive scanning
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'detectLoginFields') {
    detectLoginFields();
    sendResponse({ success: true });
  } else if (request.action === 'getPageInfo') {
    sendResponse({
      url: window.location.href,
      title: document.title,
      passwordFields: document.querySelectorAll('input[type="password"]').length
    });
  }
});

// Re-scan when URL changes (for SPA applications)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    detectLoginFields();
  }
}).observe(document, { subtree: true, childList: true });
