import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { ActivityIndicator, View } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

import ChatScreen from './screens/ChatScreen';
import SettingsScreen from './screens/SettingsScreen';
import SessionsScreen from './screens/SessionsScreen';
import { JARVISProvider } from './context/JARVISContext';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const ChatNavigator = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: '#1a1a2e',
      },
      headerTintColor: '#00d4ff',
      headerTitleStyle: {
        fontWeight: 'bold',
        fontSize: 18,
      },
    }}
  >
    <Stack.Screen
      name="ChatHome"
      component={ChatScreen}
      options={{ title: '💬 JARVIS Chat' }}
    />
  </Stack.Navigator>
);

const SessionsNavigator = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: '#1a1a2e',
      },
      headerTintColor: '#00d4ff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen
      name="SessionsList"
      component={SessionsScreen}
      options={{ title: '📋 Sessions' }}
    />
  </Stack.Navigator>
);

const SettingsNavigator = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: '#1a1a2e',
      },
      headerTintColor: '#00d4ff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen
      name="SettingsHome"
      component={SettingsScreen}
      options={{ title: '⚙️ Settings' }}
    />
  </Stack.Navigator>
);

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: '#00d4ff',
        tabBarInactiveTintColor: '#666',
        tabBarStyle: {
          backgroundColor: '#1a1a2e',
          borderTopColor: '#00d4ff',
          borderTopWidth: 1,
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Chat') {
            iconName = focused ? 'chatbubble' : 'chatbubble-outline';
          } else if (route.name === 'Sessions') {
            iconName = focused ? 'document-text' : 'document-text-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarLabel: route.name,
      })}
    >
      <Tab.Screen
        name="Chat"
        component={ChatNavigator}
        options={{ title: 'Chat' }}
      />
      <Tab.Screen
        name="Sessions"
        component={SessionsNavigator}
        options={{ title: 'Sessions' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsNavigator}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const prepare = async () => {
      try {
        // Initialize app
        setIsReady(true);
      } catch (e) {
        console.warn(e);
      }
    };

    prepare();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#1a1a2e' }}>
        <ActivityIndicator size="large" color="#00d4ff" />
      </View>
    );
  }

  return (
    <JARVISProvider>
      <NavigationContainer>
        <TabNavigator />
      </NavigationContainer>
    </JARVISProvider>
  );
}
