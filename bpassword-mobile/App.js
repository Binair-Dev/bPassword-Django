import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import LoginScreen from './src/screens/LoginScreen';
import CredentialsScreen from './src/screens/CredentialsScreen';
import CredentialDetailScreen from './src/screens/CredentialDetailScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
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
