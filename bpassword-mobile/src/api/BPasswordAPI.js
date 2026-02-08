import * as SecureStore from 'expo-secure-store';

const API_KEY_STORAGE = 'bpassword_api_key';
const API_URL_STORAGE = 'bpassword_api_url';
const DEFAULT_URL = 'https://bpassword.b-services.be/api/';

class BPasswordAPI {
  constructor() {
    this.defaultUrl = DEFAULT_URL;
  }

  async getApiKey() {
    try {
      return await SecureStore.getItemAsync(API_KEY_STORAGE);
    } catch (error) {
      console.error('Error retrieving API key:', error);
      return null;
    }
  }

  async setApiKey(apiKey) {
    try {
      await SecureStore.setItemAsync(API_KEY_STORAGE, apiKey);
    } catch (error) {
      console.error('Error saving API key:', error);
      throw error;
    }
  }

  async clearApiKey() {
    try {
      await SecureStore.deleteItemAsync(API_KEY_STORAGE);
    } catch (error) {
      console.error('Error clearing API key:', error);
    }
  }

  async getApiUrl() {
    try {
      const url = await SecureStore.getItemAsync(API_URL_STORAGE);
      const finalUrl = url || this.defaultUrl;
      return finalUrl.endsWith('/') ? finalUrl : finalUrl + '/';
    } catch (error) {
      console.error('Error retrieving API URL:', error);
      return this.defaultUrl;
    }
  }

  async setApiUrl(apiUrl) {
    try {
      await SecureStore.setItemAsync(API_URL_STORAGE, apiUrl);
    } catch (error) {
      console.error('Error saving API URL:', error);
      throw error;
    }
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
      const response = await fetch(url, {
        ...options,
        headers,
        redirect: 'follow',
        cache: 'no-store'
      });

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

  async listCredentials(query = '') {
    const endpoint = query ? `credentials/?q=${encodeURIComponent(query)}` : 'credentials';
    return this.request(endpoint, { method: 'GET' });
  }

  async getCredential(id) {
    return this.request(`credentials/${id}`, { method: 'GET' });
  }

  async createCredential(data) {
    return this.request('credentials', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateCredential(id, data) {
    return this.request(`credentials/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteCredential(id) {
    return this.request(`credentials/${id}`, { method: 'DELETE' });
  }

  async testConnection() {
    try {
      await this.request('credentials', { method: 'GET' });
      return { success: true, message: 'Connection successful!' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }
}

export default new BPasswordAPI();
