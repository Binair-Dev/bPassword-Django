import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  RefreshControl,
  Alert,
  ActivityIndicator
} from 'react-native';
import * as Clipboard from 'expo-clipboard';
import BPasswordAPI from '../api/BPasswordAPI';

export default function CredentialsScreen({ navigation }) {
  const [credentials, setCredentials] = useState([]);
  const [filteredCredentials, setFilteredCredentials] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadCredentials = useCallback(async () => {
    try {
      const data = await BPasswordAPI.listCredentials();
      setCredentials(data);
      setFilteredCredentials(data);
    } catch (error) {
      Alert.alert('Erreur', error.message);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadCredentials();
    setRefreshing(false);
  }, [loadCredentials]);

  useEffect(() => {
    loadCredentials().then(() => setLoading(false));
  }, [loadCredentials]);

  useEffect(() => {
    if (searchQuery) {
      const filtered = credentials.filter(cred =>
        cred.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cred.username?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredCredentials(filtered);
    } else {
      setFilteredCredentials(credentials);
    }
  }, [searchQuery, credentials]);

  const copyToClipboard = async (text, label) => {
    await Clipboard.setStringAsync(text);
    Alert.alert('✅ Copié', `${label} copié dans le presse-papier`);
  };

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Voulez-vous vraiment vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Oui',
          style: 'destructive',
          onPress: async () => {
            await BPasswordAPI.clearApiKey();
            navigation.replace('Login');
          }
        }
      ]
    );
  };

  const renderCredential = ({ item }) => (
    <TouchableOpacity
      style={styles.credentialCard}
      onPress={() => navigation.navigate('CredentialDetail', { credential: item })}
    >
      <View style={styles.credentialInfo}>
        <Text style={styles.credentialName}>{item.name}</Text>
        <Text style={styles.credentialUsername}>{item.username || 'Pas de username'}</Text>
        <Text style={styles.credentialUrl}>{item.url || 'Pas d\'URL'}</Text>
      </View>
      <View style={styles.credentialActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => copyToClipboard(item.username, 'Username')}
        >
          <Text style={styles.actionButtonText}>👤</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => copyToClipboard(item.password, 'Mot de passe')}
        >
          <Text style={styles.actionButtonText}>🔑</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Chargement...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="🔍 Rechercher..."
          placeholderTextColor="#999"
        />
      </View>

      <FlatList
        data={filteredCredentials}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderCredential}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>
              {searchQuery ? 'Aucun résultat trouvé' : 'Aucun mot de passe enregistré'}
            </Text>
          </View>
        }
      />

      <View style={styles.bottomActions}>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('CredentialDetail', { credential: null })}
        >
          <Text style={styles.addButtonText}>➕ Ajouter</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Text style={styles.logoutButtonText}>🚪 Déconnexion</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  searchContainer: {
    padding: 10,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  listContainer: {
    padding: 10,
  },
  credentialCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  credentialInfo: {
    flex: 1,
  },
  credentialName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  credentialUsername: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  credentialUrl: {
    fontSize: 12,
    color: '#999',
  },
  credentialActions: {
    flexDirection: 'row',
  },
  actionButton: {
    padding: 10,
    marginLeft: 5,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  actionButtonText: {
    fontSize: 20,
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
  bottomActions: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  addButton: {
    flex: 1,
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    marginRight: 10,
    alignItems: 'center',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#f44336',
    padding: 15,
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
