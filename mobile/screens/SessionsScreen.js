import React, { useFocusEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Text,
  Alert,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import { useJARVIS } from '../context/JARVISContext';

const SessionsScreen = ({ navigation }) => {
  const {
    sessions,
    loading,
    loadSessions,
    loadSessionHistory,
    deleteSession,
  } = useJARVIS();

  useFocusEffect(
    useCallback(() => {
      loadSessions();
    }, [loadSessions])
  );

  const handleSelectSession = useCallback(
    async (sessionId) => {
      try {
        await loadSessionHistory(sessionId);
        navigation.navigate('Chat', { screen: 'ChatHome' });
      } catch (error) {
        Alert.alert('Error', 'Failed to load session history');
      }
    },
    [loadSessionHistory, navigation]
  );

  const handleDeleteSession = useCallback(
    (sessionId) => {
      Alert.alert(
        'Delete Session',
        'Are you sure you want to delete this session?',
        [
          { text: 'Cancel', onPress: () => {}, style: 'cancel' },
          {
            text: 'Delete',
            onPress: async () => {
              try {
                await deleteSession(sessionId);
                await loadSessions();
              } catch (error) {
                Alert.alert('Error', 'Failed to delete session');
              }
            },
            style: 'destructive',
          },
        ]
      );
    },
    [deleteSession, loadSessions]
  );

  const renderSession = ({ item }) => {
    const createdDate = new Date(item.created_at);
    const formattedDate = createdDate.toLocaleDateString();
    const formattedTime = createdDate.toLocaleTimeString();

    return (
      <TouchableOpacity
        style={styles.sessionItem}
        onPress={() => handleSelectSession(item.id)}
      >
        <View style={styles.sessionContent}>
          <Text style={styles.sessionId}>
            {item.id.substring(0, 8)}...{item.id.substring(item.id.length - 4)}
          </Text>
          <Text style={styles.sessionMeta}>
            📅 {formattedDate} • 🕐 {formattedTime}
          </Text>
          <Text style={styles.sessionMessages}>
            💬 {item.message_count} messages
          </Text>
        </View>

        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => handleDeleteSession(item.id)}
        >
          <Icon name="trash-outline" size={20} color="#ff6b6b" />
        </TouchableOpacity>
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="chatbubbles-outline" size={60} color="#666" />
      <Text style={styles.emptyStateText}>No sessions yet</Text>
      <Text style={styles.emptyStateSubtext}>
        Start a new chat to create your first session
      </Text>
    </View>
  );

  if (loading && sessions.length === 0) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#00d4ff" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />

      <FlatList
        data={sessions}
        keyExtractor={(item) => item.id}
        renderItem={renderSession}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={
          sessions.length === 0 ? styles.emptyListContent : {}
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  sessionItem: {
    flexDirection: 'row',
    padding: 15,
    marginHorizontal: 10,
    marginVertical: 8,
    backgroundColor: '#16213e',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#00d4ff',
    alignItems: 'center',
  },
  sessionContent: {
    flex: 1,
  },
  sessionId: {
    color: '#00d4ff',
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  sessionMeta: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 4,
  },
  sessionMessages: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  deleteButton: {
    padding: 10,
    marginLeft: 10,
  },
  emptyState: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyListContent: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  emptyStateText: {
    color: '#ddd',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 16,
  },
  emptyStateSubtext: {
    color: '#888',
    fontSize: 13,
    marginTop: 8,
    textAlign: 'center',
  },
});

export default SessionsScreen;
