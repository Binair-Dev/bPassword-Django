// Service worker for Manifest V3
let isConnected = false;

// Check connection on startup
chrome.runtime.onStartup.addListener(async () => {
  await checkConnection();
});

// Check connection on install/update
chrome.runtime.onInstalled.addListener(async (details) => {
  await checkConnection();

  // Open options page if no API key is configured
  const result = await chrome.storage.local.get('apiKey');
  if (!result.apiKey) {
    chrome.runtime.openOptionsPage();
  }
});

// Handle messages from other scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getConnectionStatus') {
    sendResponse({ isConnected });
  } else if (request.action === 'updateBadge') {
    isConnected = request.connected;
    updateBadge();
  } else if (request.action === 'checkConnection') {
    checkConnection().then(() => sendResponse({ isConnected }));
    return true; // Keep message channel open for async response
  }
});

// Check connection status
async function checkConnection() {
  try {
    const result = await chrome.storage.local.get(['apiKey', 'apiUrl']);

    if (result.apiKey) {
      // Test if API key is valid format
      if (/^[a-f0-9]{64}$/i.test(result.apiKey)) {
        isConnected = true;
      } else {
        isConnected = false;
      }
    } else {
      isConnected = false;
    }
  } catch (error) {
    console.error('Error checking connection:', error);
    isConnected = false;
  }

  updateBadge();
}

// Update badge
function updateBadge() {
  const text = isConnected ? '' : '!';
  const color = isConnected ? '#4CAF50' : '#F44336';
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color });
}

// Periodic connection check (every 5 minutes)
setInterval(async () => {
  await checkConnection();
}, 5 * 60 * 1000);

// Initial connection check
checkConnection();
