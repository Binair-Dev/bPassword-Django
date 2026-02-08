import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as SplashScreen from 'expo-splash-screen';

import BPasswordAPI from './src/api/BPasswordAPI';
import LoginScreen from './src/screens/LoginScreen';
import CredentialsScreen from './src/screens/CredentialsScreen';
import CredentialDetailScreen from './src/screens/CredentialDetailScreen';

const Stack = createStackNavigator();

export default function App() {
  const [initialScreen, setInitialScreen] = useState('Login');
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    prepareApp();
  }, []);

  const prepareApp = async () => {
    try {
      // Keep splash screen visible
      await SplashScreen.preventAutoHideAsync();

      // Check if API key exists
      const apiKey = await BPasswordAPI.getApiKey();

      // Set initial screen based on API key presence
      setInitialScreen(apiKey ? 'Credentials' : 'Login');
    } catch (error) {
      console.error('Error checking auth:', error);
      setInitialScreen('Login');
    } finally {
      setIsReady(true);
      // Hide splash screen when ready
      await SplashScreen.hideAsync();
    }
  };

  if (!isReady) {
    return null; // Keep showing splash screen
  }

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName={initialScreen}
          screenOptions={{
            headerStyle: { backgroundColor: '#4CAF50' },
            headerTintColor: '#fff',
            headerTitleStyle: { fontWeight: 'bold' }
          }}
        >
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ title: 'bPassword - Connexion', headerLeft: null }}
          />
          <Stack.Screen
            name="Credentials"
            component={CredentialsScreen}
            options={{ title: 'Mes Mots de Passe', headerLeft: null }}
          />
          <Stack.Screen
            name="CredentialDetail"
            component={CredentialDetailScreen}
            options={{ title: 'Détails' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="auto" />
    </SafeAreaProvider>
  );
}
