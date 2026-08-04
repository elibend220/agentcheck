import React, { useState, useCallback } from 'react';
import {
  View,
  StyleSheet,
  StatusBar,
  Alert,
  TouchableOpacity,
  Text,
} from 'react-native';
import { GiftedChat } from 'react-native-gifted-chat';
import Icon from 'react-native-vector-icons/Ionicons';
import { useJARVIS } from '../context/JARVISContext';
import MetricsBar from '../components/MetricsBar';

const ChatScreen = ({ navigation }) => {
  const {
    messages,
    loading,
    sessionId,
    metrics,
    sendMessage,
    initializeSession,
  } = useJARVIS();

  const handleSend = useCallback(
    async (messages = []) => {
      const userMessage = messages[0].text;
      try {
        await sendMessage(userMessage);
      } catch (error) {
        Alert.alert('Error', 'Failed to send message. Please try again.');
      }
    },
    [sendMessage]
  );

  const handleNewSession = useCallback(async () => {
    try {
      await initializeSession();
      Alert.alert('Success', 'New session started!');
    } catch (error) {
      Alert.alert('Error', 'Failed to create new session');
    }
  }, [initializeSession]);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />

      {metrics && <MetricsBar metrics={metrics} />}

      <GiftedChat
        messages={messages}
        onSend={handleSend}
        user={{
          _id: 1,
          name: 'You',
        }}
        placeholder="Ask JARVIS..."
        isLoadingEarlier={loading}
        renderUsernameOnMessage={true}
        showUserAvatar={true}
        textInputProps={{
          placeholderTextColor: '#999',
        }}
        wrapInSafeArea={false}
        alwaysShowSend={true}
        renderSend={(props) => (
          <TouchableOpacity
            {...props}
            style={styles.sendButton}
            onPress={() => handleSend(props.text ? [{ text: props.text }] : [])}
            disabled={!props.text}
          >
            <Icon
              name="send"
              size={20}
              color={props.text ? '#00d4ff' : '#666'}
            />
          </TouchableOpacity>
        )}
        containerStyle={styles.chatContainer}
        inverted={true}
        timeFormat="HH:mm"
        dateFormat="DD/MM/YYYY"
        listViewProps={{
          scrollEventThrottle: 16,
        }}
      />

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.footerButton}
          onPress={handleNewSession}
        >
          <Icon name="add-circle-outline" size={20} color="#00d4ff" />
          <Text style={styles.footerButtonText}>New Session</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.footerButton}
          onPress={() => navigation.navigate('Sessions')}
        >
          <Icon name="document-text-outline" size={20} color="#00d4ff" />
          <Text style={styles.footerButtonText}>History</Text>
        </TouchableOpacity>

        <View style={styles.sessionInfo}>
          <Text style={styles.sessionText}>
            {sessionId ? `Session: ${sessionId.substring(0, 8)}...` : 'No session'}
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  chatContainer: {
    backgroundColor: '#1a1a2e',
  },
  sendButton: {
    paddingRight: 15,
    paddingLeft: 10,
    justifyContent: 'center',
  },
  footer: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 10,
    backgroundColor: '#16213e',
    borderTopColor: '#00d4ff',
    borderTopWidth: 1,
    alignItems: 'center',
  },
  footerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: 'rgba(0, 212, 255, 0.1)',
    borderRadius: 8,
    marginHorizontal: 5,
  },
  footerButtonText: {
    marginLeft: 8,
    color: '#00d4ff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  sessionInfo: {
    flex: 1,
    alignItems: 'flex-end',
  },
  sessionText: {
    color: '#888',
    fontSize: 11,
  },
});

export default ChatScreen;
