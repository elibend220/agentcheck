import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Text,
  TextInput,
  Alert,
  StatusBar,
  Switch,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useJARVIS } from '../context/JARVISContext';

const SettingsScreen = () => {
  const { apiUrl, updateApiUrl } = useJARVIS();
  const [localApiUrl, setLocalApiUrl] = useState(apiUrl);
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const savedUrl = await AsyncStorage.getItem('apiUrl');
      if (savedUrl) {
        setLocalApiUrl(savedUrl);
      }
      const savedNotifications = await AsyncStorage.getItem('notifications');
      if (savedNotifications !== null) {
        setNotifications(JSON.parse(savedNotifications));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleSaveApiUrl = async () => {
    try {
      if (!localApiUrl.trim()) {
        Alert.alert('Error', 'API URL cannot be empty');
        return;
      }

      // Validate URL format
      try {
        new URL(localApiUrl);
      } catch {
        Alert.alert('Error', 'Invalid URL format');
        return;
      }

      await updateApiUrl(localApiUrl);
      Alert.alert('Success', 'API URL updated successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to update API URL');
    }
  };

  const handleToggleNotifications = async () => {
    try {
      const newValue = !notifications;
      setNotifications(newValue);
      await AsyncStorage.setItem('notifications', JSON.stringify(newValue));
    } catch (error) {
      console.error('Failed to toggle notifications:', error);
    }
  };

  const handleResetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to defaults?',
      [
        { text: 'Cancel', onPress: () => {}, style: 'cancel' },
        {
          text: 'Reset',
          onPress: async () => {
            try {
              setLocalApiUrl('http://10.0.2.2:8000');
              setNotifications(true);
              await AsyncStorage.removeItem('apiUrl');
              await AsyncStorage.removeItem('notifications');
              await updateApiUrl('http://10.0.2.2:8000');
              Alert.alert('Success', 'Settings reset to defaults');
            } catch (error) {
              Alert.alert('Error', 'Failed to reset settings');
            }
          },
          style: 'destructive',
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />

      <ScrollView contentContainerStyle={styles.content}>
        {/* API Configuration */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="cloud-outline" size={20} color="#00d4ff" />
            <Text style={styles.sectionTitle}>Backend Configuration</Text>
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>API URL</Text>
            <TextInput
              style={styles.urlInput}
              value={localApiUrl}
              onChangeText={setLocalApiUrl}
              placeholder="Enter API URL"
              placeholderTextColor="#666"
              editable={true}
            />
            <Text style={styles.helpText}>
              Local: http://10.0.2.2:8000 (Android emulator)
              {'\n'}
              Device: http://192.168.x.x:8000 (Local WiFi)
              {'\n'}
              Remote: https://api.example.com (Production)
            </Text>
          </View>

          <TouchableOpacity
            style={styles.button}
            onPress={handleSaveApiUrl}
          >
            <Icon name="checkmark-circle" size={18} color="#fff" />
            <Text style={styles.buttonText}>Save API URL</Text>
          </TouchableOpacity>
        </View>

        {/* Preferences */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="settings-outline" size={20} color="#00d4ff" />
            <Text style={styles.sectionTitle}>Preferences</Text>
          </View>

          <View style={styles.preferencesItem}>
            <View>
              <Text style={styles.preferencesLabel}>Notifications</Text>
              <Text style={styles.preferencesSubtext}>
                Receive message notifications
              </Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={handleToggleNotifications}
              trackColor={{ false: '#767577', true: '#00d4ff' }}
              thumbColor={notifications ? '#00d4ff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.preferencesItem}>
            <View>
              <Text style={styles.preferencesLabel}>Dark Mode</Text>
              <Text style={styles.preferencesSubtext}>Always enabled</Text>
            </View>
            <Switch
              value={darkMode}
              disabled={true}
              trackColor={{ false: '#767577', true: '#00d4ff' }}
              thumbColor="#00d4ff"
            />
          </View>
        </View>

        {/* About */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="information-circle-outline" size={20} color="#00d4ff" />
            <Text style={styles.sectionTitle}>About</Text>
          </View>

          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Application</Text>
            <Text style={styles.aboutValue}>JARVIS AGI Mobile</Text>
          </View>

          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Version</Text>
            <Text style={styles.aboutValue}>1.0.0</Text>
          </View>

          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Backend</Text>
            <Text style={styles.aboutValue}>FastAPI 0.104.1</Text>
          </View>

          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Features</Text>
            <Text style={styles.aboutValue}>
              • 23 Phase Orchestration{'\n'}
              • Real-time Chat{'\n'}
              • Session Management{'\n'}
              • Consciousness Metrics
            </Text>
          </View>
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.dangerButton}
            onPress={handleResetSettings}
          >
            <Icon name="warning-outline" size={18} color="#ff6b6b" />
            <Text style={styles.dangerButtonText}>Reset All Settings</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  content: {
    padding: 15,
    paddingBottom: 30,
  },
  section: {
    marginBottom: 25,
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#00d4ff',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#00d4ff',
    marginLeft: 10,
  },
  settingItem: {
    marginBottom: 12,
  },
  settingLabel: {
    color: '#ddd',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  urlInput: {
    backgroundColor: '#0f3460',
    color: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    borderWidth: 1,
    borderColor: '#00d4ff',
    marginBottom: 8,
  },
  helpText: {
    color: '#888',
    fontSize: 11,
    fontStyle: 'italic',
    lineHeight: 16,
  },
  button: {
    flexDirection: 'row',
    backgroundColor: '#00d4ff',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#1a1a2e',
    fontWeight: 'bold',
    marginLeft: 8,
    fontSize: 14,
  },
  preferencesItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 212, 255, 0.1)',
  },
  preferencesLabel: {
    color: '#ddd',
    fontSize: 14,
    fontWeight: '600',
  },
  preferencesSubtext: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  aboutItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0, 212, 255, 0.1)',
  },
  aboutLabel: {
    color: '#00d4ff',
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 4,
  },
  aboutValue: {
    color: '#aaa',
    fontSize: 12,
    lineHeight: 18,
  },
  dangerButton: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255, 107, 107, 0.1)',
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#ff6b6b',
  },
  dangerButtonText: {
    color: '#ff6b6b',
    fontWeight: 'bold',
    marginLeft: 8,
    fontSize: 14,
  },
});

export default SettingsScreen;
