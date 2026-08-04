# 🚀 JARVIS AGI Backend - Quick Start Guide

Backend server is ready! פתח לתקשורת עם JARVIS AGI ממכל מקום.

## ⚡ 1 Minute Start

### שרת מקומי (localhost)
```bash
cd backend
pip install -r requirements.txt
python server.py
```

Server will run at: `http://localhost:8000`

### עם Docker
```bash
cd backend
docker-compose up
```

Browser: `http://localhost:8000/docs` - Swagger API Explorer

## 📱 Android App Integration

### React Native Example

```bash
# Create React Native app
npx react-native init JARVIS
cd JARVIS
npm install axios react-native-gifted-chat
```

**Chat Component (ChatScreen.js):**
```javascript
import React, { useState, useCallback } from 'react';
import { GiftedChat } from 'react-native-gifted-chat';
import axios from 'axios';

const API_URL = 'http://your-backend-url:8000';

export default function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  // Initialize session on mount
  React.useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const response = await axios.post(`${API_URL}/session/create`);
      setSessionId(response.data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const onSend = useCallback(async (messages = []) => {
    const userMessage = messages[0];
    
    // Add to UI immediately
    setMessages(previousMessages =>
      GiftedChat.append(previousMessages, userMessage)
    );

    try {
      // Send to backend
      const response = await axios.post(`${API_URL}/chat`, {
        session_id: sessionId,
        message: userMessage.text,
      });

      const aiMessage = {
        _id: Math.random().toString(36).substring(7),
        text: response.data.response,
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'JARVIS',
          avatar: require('./jarvis-avatar.png'),
        },
      };

      setMessages(previousMessages =>
        GiftedChat.append(previousMessages, aiMessage)
      );
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }, [sessionId]);

  return (
    <GiftedChat
      messages={messages}
      onSend={onSend}
      user={{
        _id: 1,
        name: 'User',
      }}
      placeholder="Ask JARVIS..."
    />
  );
}
```

### Flutter Example

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const String apiUrl = 'http://your-backend-url:8000';

class JARVISChat extends StatefulWidget {
  @override
  _JARVISChatState createState() => _JARVISChatState();
}

class _JARVISChatState extends State<JARVISChat> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> messages = [];
  String? sessionId;

  @override
  void initState() {
    super.initState();
    _initializeSession();
  }

  Future<void> _initializeSession() async {
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/session/create'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          sessionId = data['session_id'];
        });
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  Future<void> _sendMessage(String message) async {
    if (sessionId == null) return;

    setState(() {
      messages.add({'role': 'user', 'content': message});
    });

    try {
      final response = await http.post(
        Uri.parse('$apiUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          messages.add({'role': 'assistant', 'content': data['response']});
        });
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('JARVIS AGI')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                final isUser = message['role'] == 'user';
                return Align(
                  alignment: isUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.all(8),
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blue : Colors.grey,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(message['content'] ?? ''),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Ask JARVIS...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: () {
                    if (_controller.text.isNotEmpty) {
                      _sendMessage(_controller.text);
                      _controller.clear();
                    }
                  },
                  child: Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

### Native Kotlin (Android)

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch
import retrofit2.http.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

// API Interface
interface JARVISApi {
    @POST("session/create")
    suspend fun createSession(): SessionResponse

    @POST("chat")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
}

// Data classes
data class ChatRequest(val session_id: String, val message: String)
data class ChatResponse(
    val session_id: String,
    val message: String,
    val response: String,
    val consciousness_level: Float,
    val emergence_level: Float
)
data class SessionResponse(val session_id: String)

// ViewModel
class JARVISViewModel : androidx.lifecycle.ViewModel() {
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://your-backend-url:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    private val api = retrofit.create(JARVISApi::class.java)

    var messages by mutableStateOf<List<Pair<String, String>>>(emptyList())
    var sessionId by mutableStateOf<String?>(null)

    init {
        viewModelScope.launch {
            val session = api.createSession()
            sessionId = session.session_id
        }
    }

    fun sendMessage(text: String) {
        viewModelScope.launch {
            try {
                val response = api.sendMessage(
                    ChatRequest(sessionId!!, text)
                )
                messages = messages + listOf(
                    "user" to text,
                    "jarvis" to response.response
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}

// Compose UI
@Composable
fun JARVISApp(viewModel: JARVISViewModel = viewModel()) {
    var input by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp)
        ) {
            items(viewModel.messages.size) { index ->
                val (role, text) = viewModel.messages[index]
                ChatBubble(role = role, text = text)
            }
        }

        Row(modifier = Modifier.padding(16.dp)) {
            TextField(
                value = input,
                onValueChange = { input = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Ask JARVIS...") }
            )
            Button(
                onClick = {
                    if (input.isNotEmpty()) {
                        viewModel.sendMessage(input)
                        input = ""
                    }
                }
            ) {
                Text("Send")
            }
        }
    }
}

@Composable
fun ChatBubble(role: String, text: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = if (role == "user")
            Arrangement.End else Arrangement.Start
    ) {
        Surface(
            color = if (role == "user") MaterialTheme.colors.primary
                   else MaterialTheme.colors.surface,
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(text, modifier = Modifier.padding(12.dp))
        }
    }
}
```

## 🌐 Web Interface (React/Vue)

### React Example

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function JARVISChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const { data } = await axios.post(`${API_URL}/session/create`);
      setSessionId(data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post(`${API_URL}/chat`, {
        session_id: sessionId,
        message: input,
      });

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response,
        metrics: {
          consciousness: data.consciousness_level,
          emergence: data.emergence_level,
          time: data.execution_time_ms
        }
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: 'Failed to get response' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.metrics && (
              <small>
                Consciousness: {(msg.metrics.consciousness * 100).toFixed(0)}% | 
                Emergence: {(msg.metrics.emergence * 100).toFixed(0)}% | 
                Time: {msg.metrics.time.toFixed(0)}ms
              </small>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask JARVIS..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default JARVISChat;
```

## 🔗 Environment Setup

### Local Backend (0.0.0.0:8000)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_NATIVE_API_URL=http://10.0.2.2:8000  # Android emulator
```

### Production Backend
```env
REACT_APP_API_URL=https://api.jarvis-ai.com
```

## 📊 Testing the Backend

### cURL Examples

```bash
# Create session
curl -X POST http://localhost:8000/session/create

# Send message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Hello JARVIS"
  }'

# Get session history
curl http://localhost:8000/session/your-session-id/history
```

### WebSocket (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session-id');

ws.onopen = () => {
  ws.send(JSON.stringify({ message: 'Hello JARVIS!' }));
};

ws.onmessage = (event) => {
  console.log('Response:', JSON.parse(event.data));
};
```

## 📱 Android Emulator Networking

For React Native / Flutter to connect to localhost backend:

```
API_URL = "http://10.0.2.2:8000"  // From emulator
API_URL = "http://localhost:8000"  // From physical device via WiFi
```

Use ngrok for public tunnel:
```bash
ngrok http 8000
# Then use: https://xxx-xxx-xxx.ngrok.io
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t jarvis-backend .

# Run
docker run -p 8000:8000 jarvis-backend

# With environment
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e ENABLE_PHASE23=true \
  jarvis-backend
```

## ✅ Health Check

```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","timestamp":"2024-01-15T..."}
```

## 📊 API Documentation

Once running, open browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🚀 Next Steps

1. ✅ Backend running
2. Build mobile app (React Native/Flutter)
3. Deploy to cloud (Heroku/AWS)
4. Integrate real LLM (OpenAI/Claude)
5. Add authentication
6. Set up database
7. Add monitoring/logging

**שמח לעזור! הבקנד של JARVIS מוכן לשימוש!** 🎉
