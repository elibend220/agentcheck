# 🔌 JARVIS Integrated API Documentation

Complete API reference for the integrated JARVIS AGI backend with user sandboxing, offline support, and autonomous search.

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Session Management](#session-management)
4. [Chat](#chat)
5. [Search](#search)
6. [Offline Support](#offline-support)
7. [System Status](#system-status)
8. [WebSocket](#websocket)
9. [Error Handling](#error-handling)
10. [Example Workflows](#example-workflows)

---

## Authentication

Currently, no authentication is required. In production, add JWT or OAuth2.

**TODO**: Add bearer token authentication
```bash
# Header required in production
Authorization: Bearer <token>
```

---

## User Management

### Create User

Create a new user sandbox for data isolation.

**Endpoint:** `POST /users/create`

**Request:**
```json
{
  "username": "alice",
  "email": "alice@example.com"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "email": "alice@example.com",
  "message": "User sandbox created"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/users/create \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com"}'
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/users/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'alice',
    email: 'alice@example.com'
  })
});
const user = await response.json();
console.log(user.user_id); // Save this!
```

---

### Get User Info

Retrieve user information and statistics.

**Endpoint:** `GET /users/{user_id}`

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "email": null,
  "created_at": "2024-01-15T10:30:00.000000",
  "sessions_count": 3
}
```

**cURL:**
```bash
curl http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000
```

---

### Get User Statistics

Get detailed user statistics.

**Endpoint:** `GET /users/{user_id}/stats`

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "total_sessions": 3,
  "total_messages": 45,
  "total_searches": 12,
  "active_sessions": [
    "session-id-1",
    "session-id-2"
  ]
}
```

---

### Delete User (GDPR)

Permanently delete user and all their data.

**Endpoint:** `DELETE /users/{user_id}`

**Response:**
```json
{
  "message": "User data deleted successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Warning:** This is irreversible!

```bash
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000
```

---

## Session Management

### Create User Session

Create a new session within a user's sandbox.

**Endpoint:** `POST /users/{user_id}/sessions/create`

**Response:**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/sessions/create
```

---

### Get User Session

Get session information.

**Endpoint:** `GET /users/{user_id}/sessions/{session_id}`

**Response:**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00.000000",
  "message_count": 12
}
```

---

### Get Session History

Get all messages in a session.

**Endpoint:** `GET /users/{user_id}/sessions/{session_id}/history`

**Response:**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00.000000",
  "messages": [
    {
      "role": "user",
      "content": "Hello JARVIS",
      "timestamp": "2024-01-15T10:30:01.000000"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "timestamp": "2024-01-15T10:30:02.000000"
    }
  ],
  "search_queries": []
}
```

---

## Chat

### Send Message (User Sandboxed)

Send a message with user sandboxing and optional autonomous search.

**Endpoint:** `POST /chat`

**Request:**
```json
{
  "message": "What are the latest AI developments?",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "offline_mode": false,
  "enable_phases": {
    "enable_phase19": true,
    "enable_phase20": true
  }
}
```

**Response:**
```json
{
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "message": "What are the latest AI developments?",
  "response": "Based on recent developments...",
  "phases_executed": ["Phase 1", "Phase 2", ..., "Phase 23"],
  "consciousness_level": 0.87,
  "emergence_level": 0.72,
  "confidence_score": 0.91,
  "execution_time_ms": 1234.5,
  "timestamp": "2024-01-15T10:30:02.000000"
}
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What are the latest AI developments?',
    user_id: user_id,
    session_id: session_id,
    offline_mode: false
  })
});

const result = await response.json();
console.log('JARVIS:', result.response);
console.log('Consciousness:', result.consciousness_level);
console.log('Time:', result.execution_time_ms, 'ms');
```

**Features:**
- ✓ Automatic session creation if needed
- ✓ Autonomous search for information requests
- ✓ Full 23-phase orchestration
- ✓ Message saved to user sandbox
- ✓ Search results recorded
- ✓ Offline mode support

---

## Search

### Search (On-Demand or Autonomous)

Perform a search for information.

**Endpoint:** `POST /search`

**Request (On-Demand):**
```json
{
  "query": "machine learning algorithms",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "autonomous": false,
  "use_cache": true,
  "offline_mode": false
}
```

**Request (Autonomous - called by system):**
```json
{
  "query": "latest AI trends",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "autonomous": true,
  "use_cache": true,
  "offline_mode": false
}
```

**Response:**
```json
{
  "query": "machine learning algorithms",
  "results": [
    {
      "title": "Supervised Learning Algorithms",
      "url": "https://example.com/ml-algorithms",
      "snippet": "Overview of supervised learning...",
      "source": "example.com"
    }
  ],
  "source": "web",
  "autonomous": false,
  "timestamp": "2024-01-15T10:30:02.000000",
  "result_count": 5
}
```

**Search Sources:**
- `"web"` - Fresh web search
- `"cache"` - Previously cached result
- `"offline"` - Local cache (no internet)

---

### Get Search Cache Stats

Get search cache statistics.

**Endpoint:** `GET /search/cache-stats`

**Response:**
```json
{
  "cached_queries": 142,
  "total_searches": 1003,
  "cache_size_bytes": 524288
}
```

---

## Offline Support

### Sync Offline Data

Sync queued actions when connection is restored.

**Endpoint:** `POST /sync`

**Request:**
```json
[
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "action": "send_message",
    "data": {
      "content": "Hello from offline",
      "action_id": "action-123"
    },
    "timestamp": "2024-01-15T10:30:00.000000"
  }
]
```

**Response:**
```json
{
  "synced_count": 1,
  "total_actions": 1,
  "message": "Offline data synced"
}
```

---

### Get Offline Statistics

Get offline storage statistics.

**Endpoint:** `GET /offline/stats`

**Response:**
```json
{
  "offline_messages": 25,
  "cached_searches": 12,
  "pending_syncs": 3,
  "db_file": "jarvis_offline.db"
}
```

---

### Toggle Offline Mode

Enable/disable offline mode for a user.

**Endpoint:** `POST /offline/mode/{user_id}`

**Request:**
```json
{
  "offline": true
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "offline_mode": true
}
```

**Note:** When offline, only cached searches are available.

---

## System Status

### Get System Status

Get comprehensive system status including infrastructure metrics.

**Endpoint:** `GET /status`

**Response:**
```json
{
  "status": "online",
  "version": "1.0.0",
  "phases_enabled": 23,
  "uptime_seconds": 3600.5,
  "sessions_active": 5,
  "infrastructure": {
    "user_sandboxing": {
      "enabled": true,
      "users": 12,
      "total_user_sessions": 34,
      "total_messages": 892
    },
    "offline_support": {
      "enabled": true,
      "cached_messages": 145,
      "cached_searches": 67,
      "pending_syncs": 2
    },
    "search": {
      "enabled": true,
      "cache_size": 2097152,
      "cached_queries": 142,
      "total_searches": 1003
    }
  }
}
```

---

### Health Check

Quick health check.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

## WebSocket

### Real-Time Chat with User Sandboxing

Connect via WebSocket for real-time messaging.

**URL:** `ws://localhost:8000/ws/{session_id}?user_id={user_id}`

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/660e8400-e29b-41d4-a716-446655440001?user_id=550e8400-e29b-41d4-a716-446655440000');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    message: 'Hello JARVIS'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connection') {
    console.log('Connection established:', data);
  } else if (data.type === 'response') {
    console.log('Response:', data.message);
    console.log('Consciousness:', data.consciousness_level);
  } else if (data.type === 'error') {
    console.error('Error:', data.message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

**Message Types:**

**Connection:**
```json
{
  "type": "connection",
  "status": "connected",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Connected to JARVIS AGI System"
}
```

**Processing:**
```json
{
  "type": "processing",
  "status": "analyzing"
}
```

**Response:**
```json
{
  "type": "response",
  "status": "complete",
  "message": "Response text...",
  "consciousness_level": 0.87,
  "emergence_level": 0.72,
  "execution_time_ms": 1234.5,
  "timestamp": "2024-01-15T10:30:02.000000"
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## Error Handling

### Error Responses

**404 Not Found:**
```json
{
  "detail": "User not found"
}
```

**403 Forbidden:**
```json
{
  "detail": "Access denied"
}
```

**400 Bad Request:**
```json
{
  "detail": "Invalid request"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error description"
}
```

---

## Example Workflows

### Complete User Journey

```javascript
// 1. Create user
const userRes = await fetch('http://localhost:8000/users/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'alice', email: 'alice@example.com' })
});
const { user_id } = await userRes.json();
console.log('Created user:', user_id);

// 2. Create session
const sessionRes = await fetch(`http://localhost:8000/users/${user_id}/sessions/create`, {
  method: 'POST'
});
const { session_id } = await sessionRes.json();
console.log('Created session:', session_id);

// 3. Send first message
const chatRes = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What are the latest AI developments?',
    user_id: user_id,
    session_id: session_id
  })
});
const chat1 = await chatRes.json();
console.log('Response:', chat1.response);
console.log('Consciousness:', chat1.consciousness_level);

// 4. Send another message (autonomous search may trigger)
const chat2Res = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Tell me about machine learning algorithms',
    user_id: user_id,
    session_id: session_id
  })
});
const chat2 = await chat2Res.json();
console.log('Response:', chat2.response);

// 5. Get session history
const historyRes = await fetch(`http://localhost:8000/users/${user_id}/sessions/${session_id}/history`);
const history = await historyRes.json();
console.log('Messages in session:', history.messages.length);
console.log('Searches performed:', history.search_queries.length);

// 6. Get user statistics
const statsRes = await fetch(`http://localhost:8000/users/${user_id}/stats`);
const stats = await statsRes.json();
console.log('Total messages:', stats.total_messages);
console.log('Total searches:', stats.total_searches);
```

### Offline Workflow

```javascript
// 1. Detect offline
window.addEventListener('offline', async () => {
  console.log('Going offline...');
  
  // 2. Enable offline mode
  await fetch(`http://localhost:8000/offline/mode/${user_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ offline: true })
  });

  // 3. Queue message for sync
  const syncQueue = [
    {
      user_id: user_id,
      session_id: session_id,
      action: 'send_message',
      data: {
        content: 'Hello from offline',
        action_id: 'action-' + Date.now()
      },
      timestamp: new Date().toISOString()
    }
  ];
  localStorage.setItem('pendingSyncs', JSON.stringify(syncQueue));
});

// 4. Detect online - sync data
window.addEventListener('online', async () => {
  console.log('Back online, syncing...');
  
  const pendingSyncs = JSON.parse(localStorage.getItem('pendingSyncs') || '[]');
  if (pendingSyncs.length > 0) {
    await fetch('http://localhost:8000/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pendingSyncs)
    });
    
    localStorage.removeItem('pendingSyncs');
    console.log('Synced!');
  }
  
  // Disable offline mode
  await fetch(`http://localhost:8000/offline/mode/${user_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ offline: false })
  });
});
```

### WebSocket Real-Time Chat

```javascript
// Connect with user context
const user_id = '550e8400-e29b-41d4-a716-446655440000';
const session_id = '660e8400-e29b-41d4-a716-446655440001';
const ws = new WebSocket(`ws://localhost:8000/ws/${session_id}?user_id=${user_id}`);

ws.onopen = () => {
  // Send message
  ws.send(JSON.stringify({
    message: 'Real-time conversation'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'response') {
    console.log('JARVIS:', data.message);
    console.log('Metrics:', {
      consciousness: data.consciousness_level,
      emergence: data.emergence_level,
      time: data.execution_time_ms + 'ms'
    });
    
    // Autonomous search may have occurred
    // Check user sandbox for search results
    fetchUserStats(user_id);
  }
};
```

---

## Production Checklist

- [ ] Add authentication (JWT/OAuth2)
- [ ] Add rate limiting
- [ ] Add request validation
- [ ] Enable HTTPS/WSS
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Add API versioning
- [ ] Document error codes
- [ ] Set up logging pipeline

---

## Support

For issues or questions:
1. Check this documentation
2. Review system logs: `docker-compose logs -f`
3. Check backend health: `curl http://localhost:8000/health`
4. Check status: `curl http://localhost:8000/status`
