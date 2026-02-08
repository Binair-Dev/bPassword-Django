import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView
} from 'react-native';
import BPasswordAPI from '../api/BPasswordAPI';

export default function LoginScreen({ navigation }) {
  const [apiKey, setApiKey] = useState('');
  const [apiUrl, setApiUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    // Load saved settings on mount
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const savedUrl = await BPasswordAPI.getApiUrl();
    setApiUrl(savedUrl.replace(/\/$/, '')); // Remove trailing slash for display
  };

  const validateApiKey = (key) => {
    return key && key.length === 64 && /^[a-fA-F0-9]+$/.test(key);
  };

  const handleTestConnection = async () => {
    if (!validateApiKey(apiKey)) {
      Alert.alert('Erreur', 'La clé API doit faire exactement 64 caractères hexadécimaux');
      return;
    }

    setTesting(true);
    try {
      await BPasswordAPI.setApiKey(apiKey);
      if (apiUrl) {
        await BPasswordAPI.setApiUrl(apiUrl);
      }

      const result = await BPasswordAPI.testConnection();
      if (result.success) {
        Alert.alert('Succès', 'Connexion réussie !');
      } else {
        Alert.alert('Erreur', result.message);
      }
    } catch (error) {
      Alert.alert('Erreur', error.message);
    } finally {
      setTesting(false);
    }
  };

  const handleLogin = async () => {
    if (!validateApiKey(apiKey)) {
      Alert.alert('Erreur', 'La clé API doit faire exactement 64 caractères hexadécimaux');
      return;
    }

    setLoading(true);
    try {
      await BPasswordAPI.setApiKey(apiKey);
      if (apiUrl) {
        await BPasswordAPI.setApiUrl(apiUrl);
      }

      const result = await BPasswordAPI.testConnection();
      if (result.success) {
        navigation.replace('Credentials');
      } else {
        Alert.alert('Erreur de connexion', result.message);
      }
    } catch (error) {
      Alert.alert('Erreur', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.logoContainer}>
          <Text style={styles.logo}>🔐</Text>
          <Text style={styles.title}>bPassword</Text>
          <Text style={styles.subtitle}>Gestionnaire de mots de passe</Text>
        </View>

        <View style={styles.formContainer}>
          <Text style={styles.label}>Clé API (64 caractères)</Text>
          <TextInput
            style={styles.input}
            value={apiKey}
            onChangeText={setApiKey}
            placeholder="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
            maxLength={64}
          />

          <Text style={styles.label}>URL API (optionnel)</Text>
          <TextInput
            style={styles.input}
            value={apiUrl}
            onChangeText={setApiUrl}
            placeholder="https://bpassword.b-services.be/api"
            placeholderTextColor="#999"
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
          />

          <TouchableOpacity
            style={[styles.button, styles.testButton]}
            onPress={handleTestConnection}
            disabled={testing}
          >
            {testing ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>🔗 Tester la connexion</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.loginButton]}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>✅ Se connecter</Text>
            )}
          </TouchableOpacity>
        </View>

        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>
            💡 Comment obtenir votre clé API :
          </Text>
          <Text style={styles.infoText}>
            1. Connectez-vous sur bPassword via l'extension
          </Text>
          <Text style={styles.infoText}>
            2. Allez dans Paramètres → Clés API
          </Text>
          <Text style={styles.infoText}>
            3. Copiez la clé de 64 caractères
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    fontSize: 64,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  formContainer: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 15,
    backgroundColor: '#fafafa',
  },
  button: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  testButton: {
    backgroundColor: '#2196F3',
  },
  loginButton: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  infoContainer: {
    marginTop: 30,
    padding: 15,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1565c0',
    marginBottom: 5,
  },
});
