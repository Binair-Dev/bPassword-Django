class BPasswordAPI {
  constructor() {
    this.defaultUrl = 'https://bpassword.b-services.be/api/';
  }

  async getApiKey() {
    const result = await chrome.storage.local.get('apiKey');
    return result.apiKey;
  }

  async setApiKey(apiKey) {
    await chrome.storage.local.set({ apiKey });
  }

  async getApiUrl() {
    const result = await chrome.storage.local.get('apiUrl');
    return result.apiUrl || this.defaultUrl;
  }

  async request(endpoint, options = {}) {
    const apiKey = await this.getApiKey();
    const baseUrl = await this.getApiUrl();

    if (!apiKey) {
      throw new Error('API Key not configured');
    }

    const url = `${baseUrl}${endpoint}`;
    const headers = {
      'Authorization': `Api-Key ${apiKey}`,
      'Content-Type': 'application/json',
      ...options.headers
    };

    try {
      const response = await fetch(url, { ...options, headers });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Invalid API Key');
        } else if (response.status === 403) {
          throw new Error('Access forbidden');
        } else if (response.status === 404) {
          throw new Error('Resource not found');
        } else if (response.status === 429) {
          throw new Error('Rate limit exceeded');
        } else {
          const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
          throw new Error(errorData.detail || 'Request failed');
        }
      }

      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error. Check your connection and API URL.');
      }
      throw error;
    }
  }

  // List credentials (with optional search)
  async listCredentials(query = '') {
    const endpoint = query ? `credentials/?q=${encodeURIComponent(query)}` : 'credentials';
    return this.request(endpoint, { method: 'GET' });
  }

  // Get single credential
  async getCredential(id) {
    return this.request(`credentials/${id}/`, { method: 'GET' });
  }

  // Create credential
  async createCredential(data) {
    return this.request('credentials/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Update credential
  async updateCredential(id, data) {
    return this.request(`credentials/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Delete credential
  async deleteCredential(id) {
    return this.request(`credentials/${id}/`, { method: 'DELETE' });
  }

  // Test connection
  async testConnection() {
    try {
      await this.request('credentials/', { method: 'GET' });
      return { success: true, message: 'Connection successful!' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }
}

const api = new BPasswordAPI();
