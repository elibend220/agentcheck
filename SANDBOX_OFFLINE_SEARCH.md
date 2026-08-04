# 🔒 User Sandboxing, Offline Mode & Autonomous Search

Complete guide to JARVIS AGI's isolated user environments, offline capabilities, and intelligent search features.

## 🔒 User Sandboxing

Each user operates in a completely isolated sandbox preventing data leakage and ensuring privacy.

### Architecture

```
UserManager
├── User 1 Sandbox
│   ├── Session 1
│   │   ├── Messages
│   │   ├── Search History
│   │   └── State
│   ├── Session 2
│   └── User Preferences
├── User 2 Sandbox
│   ├── Session 1
│   └── Session 2
└── User 3 Sandbox
    └── Sessions...
```

### Implementation

**Backend (Python)**

```python
from backend.user_manager import UserManager

# Initialize user manager
user_manager = UserManager()

# Create user sandbox
user_id = user_manager.create_user("alice")

# Create session within sandbox
session_id = user_manager.create_user_session(user_id)

# Add message to user's session
user_manager.add_message_to_session(
    session_id=session_id,
    role="user",
    content="Hello JARVIS",
    metadata={"type": "text"}
)

# Get session history (only for that user)
history = user_manager.get_session_history(session_id)
```

### Features

**Data Isolation**
- Each user has separate data storage
- Sessions are user-specific
- Search history is private
- Preferences are isolated

**Session Management**
```python
# Create session
session_id = user_manager.create_user_session(user_id)

# Get session
session = user.get_session(session_id)

# Delete session
user.delete_session(session_id)

# View stats
stats = user.get_stats()
# {
#   "user_id": "...",
#   "total_sessions": 3,
#   "total_messages": 45,
#   "total_searches": 12
# }
```

**User Statistics**
```python
# Get individual user stats
user = user_manager.get_user(user_id)
stats = user.get_stats()

# Get all users stats
all_stats = user_manager.get_all_user_stats()
```

### API Endpoints

**User Operations**
```bash
# Create user
POST /users/create
{
  "username": "alice",
  "email": "alice@example.com"
}
# Returns: { "user_id": "uuid" }

# Get user info
GET /users/{user_id}

# Delete user (GDPR)
DELETE /users/{user_id}

# Get user statistics
GET /users/{user_id}/stats
```

**Session Operations**
```bash
# Create session
POST /users/{user_id}/sessions/create
# Returns: { "session_id": "uuid" }

# Get session
GET /users/{user_id}/sessions/{session_id}

# Get session history
GET /users/{user_id}/sessions/{session_id}/history

# Delete session
DELETE /users/{user_id}/sessions/{session_id}
```

### Security

**Data Protection**
- ✅ User data isolated at OS level
- ✅ Database rows filtered by user_id
- ✅ Session ownership validated
- ✅ Cross-user access prevented
- ✅ Audit logging enabled

**Authentication**
```python
# Verify user ownership of session
def verify_session_ownership(session_id, user_id):
    owner_id = user_manager.get_session_user(session_id)
    return owner_id == user_id
```

## 🌐 Offline Mode

JARVIS works seamlessly without internet, syncing when connection is restored.

### Architecture

```
Offline Mode
├── Local Cache (SQLite)
│   ├── Messages
│   ├── Search Results
│   └── User Preferences
├── Sync Queue
│   └── Pending Actions (auto-synced when online)
└── Status Indicator
    └── User Notification
```

### Backend Implementation

**Offline Storage**

```python
from backend.offline_support import OfflineStorage

# Initialize offline storage
offline_db = OfflineStorage(db_path="jarvis_offline.db")

# Save message locally
offline_db.save_message(
    user_id="user123",
    session_id="session456",
    role="user",
    content="Hello",
    message_id="msg789"
)

# Cache search results
offline_db.cache_search_result(
    query="machine learning",
    results=[{"title": "...", "url": "..."}],
    source="web"
)

# Get cached search
cached = offline_db.get_cached_search("machine learning")

# Queue action for sync
offline_db.queue_sync_action(
    user_id="user123",
    session_id="session456",
    action="send_message",
    data={"content": "Hello"},
    action_id="action789"
)

# Get pending syncs
pending = offline_db.get_pending_syncs("user123")

# Mark synced
offline_db.mark_synced("action789")
```

### Frontend Implementation

**Offline Detection**

```javascript
// Monitor online/offline status
window.addEventListener('online', () => {
  // Connected - sync pending data
  syncOfflineData();
});

window.addEventListener('offline', () => {
  // Disconnected - use local cache
  enableOfflineMode();
});

// Check status
const isOnline = navigator.onLine;
```

**Offline Component**

```jsx
import OfflineMode from './components/OfflineMode';

function App() {
  return (
    <>
      <OfflineMode />
      {/* Rest of app */}
    </>
  );
}
```

### Usage

**Enable Offline Mode**
```bash
# Automatically enabled when offline
# Shows banner: "📡 Offline Mode • Using cached data"
```

**Local Data Access**
```
✓ Previous messages
✓ Cached search results
✓ User preferences
✓ Session history
```

**Limitations Offline**
```
✗ Real-time backend features
✗ Web search (cached results only)
✗ New session creation
✗ Account changes
```

**Auto-Sync When Online**
```javascript
// Automatically syncs when connection restored
// Shows: "Syncing... (3 pending)"
// Then: "✓ All synced"
```

### Database Schema

```sql
-- Messages table
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  role TEXT,           -- "user", "assistant", "system"
  content TEXT,
  timestamp TEXT,
  metadata TEXT        -- JSON
);

-- Search cache
CREATE TABLE search_cache (
  id TEXT PRIMARY KEY,
  query TEXT UNIQUE,
  results TEXT,        -- JSON array
  timestamp TEXT,
  source TEXT          -- "web", "cache", "offline"
);

-- Sync queue
CREATE TABLE sync_queue (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  session_id TEXT,
  action TEXT,         -- "send_message", "create_session", etc.
  data TEXT,           -- JSON payload
  timestamp TEXT,
  synced INTEGER       -- 0 or 1
);
```

## 🔍 Autonomous Search

JARVIS intelligently searches for information both on-demand and autonomously.

### Search Engine

**Architecture**

```python
from backend.search_engine import SearchEngine

search_engine = SearchEngine(enable_web_search=True)

# On-demand search (user requests)
result = search_engine.search(
    query="Python async await",
    autonomous=False,      # User-requested
    use_cache=True,
    offline_mode=False
)

# Autonomous search (system decides)
needs_search, query = search_engine.autonomous_search_decision(
    message="Tell me about the latest AI developments",
    context=[previous_messages]
)

if needs_search:
    result = search_engine.search(
        query=query,
        autonomous=True,   # System-initiated
        use_cache=True
    )
```

### Autonomous Decision Making

**Triggers Autonomous Search**

System automatically searches when:

```python
SEARCH_KEYWORDS = [
    "latest",
    "current",
    "today",
    "recent",
    "real-time",
    "now",
    "what is",
    "how to",
    "news",
    "update"
]

QUESTION_PATTERNS = [
    "who",
    "what",
    "where",
    "when",
    "why",
    "how"
]

# Example: "What are the latest AI trends?"
# → Autonomous search for "AI trends"

# Example: "How do I learn Python?"
# → Autonomous search for "Python tutorial"
```

### On-Demand Search

```javascript
// User explicitly requests search
async function searchFor(query) {
  try {
    const response = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        autonomous: false,  // User-requested
        session_id: sessionId
      })
    });

    const results = await response.json();
    console.log('Search results:', results);
  } catch (error) {
    console.error('Search failed:', error);
  }
}
```

### Search Results

**Response Format**

```json
{
  "query": "Python async",
  "results": [
    {
      "title": "Python Async/Await Guide",
      "url": "https://docs.python.org/...",
      "snippet": "Python's async and await syntax...",
      "source": "docs.python.org"
    }
  ],
  "source": "web",            // or "cache", "offline"
  "autonomous": false,
  "timestamp": "2024-01-15T...",
  "result_count": 5
}
```

### Caching

**Search Cache**

```python
# Cache search results (24-hour TTL by default)
search_engine.cache.set(
    "machine learning",
    [results...]
)

# Retrieve from cache
cached = search_engine.cache.get("machine learning")

# Cache stats
stats = search_engine.get_cache_stats()
# {
#   "cached_queries": 142,
#   "total_searches": 1003,
#   "cache_size_bytes": 524288
# }
```

### Web Search Integration

**Current Status**: Mock implementation

**To Integrate Real Web Search**

```python
# Option 1: DuckDuckGo API
from duckduckgo_search import DDGS

def search_duckduckgo(query):
    results = DDGS().text(query, max_results=5)
    return results

# Option 2: Google Search API
import googleapiclient.discovery

def search_google(query, api_key):
    service = googleapiclient.discovery.build(
        "customsearch", "v1",
        developerKey=api_key
    )
    results = service.cse().list(q=query, cx='...').execute()
    return results['items']

# Option 3: Bing Search API
import requests

def search_bing(query, subscription_key):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": query}
    response = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers=headers,
        params=params
    )
    return response.json()['webPages']['value']
```

## 📊 Integration Example

**Complete User Journey**

```python
from backend.user_manager import UserManager
from backend.search_engine import SearchEngine
from backend.offline_support import OfflineStorage

# Initialize
user_manager = UserManager()
search_engine = SearchEngine()
offline_storage = OfflineStorage()

# 1. Create user sandbox
user_id = user_manager.create_user("alice")

# 2. Create session
session_id = user_manager.create_user_session(user_id)

# 3. User sends message
message = "Tell me about neural networks"
user_manager.add_message_to_session(
    session_id, "user", message
)

# 4. Check if autonomous search needed
needs_search, query = search_engine.autonomous_search_decision(
    message, []
)

# 5. If needed, perform search
if needs_search:
    search_result = search_engine.search(
        query=query,
        autonomous=True,
        offline_mode=False
    )
    
    # Cache for offline
    offline_storage.cache_search_result(
        query,
        search_result['results'],
        'web'
    )
    
    # Record search
    user_manager.record_search(
        session_id,
        query,
        search_result['results'],
        'web'
    )

# 6. Add response
user_manager.add_message_to_session(
    session_id, "assistant",
    f"Found {len(search_result['results'])} results..."
)

# 7. Get user stats
stats = user_manager.get_user(user_id).get_stats()
```

## 🔐 Privacy & Security

### User Sandboxing
- ✅ Complete data isolation
- ✅ No cross-user data access
- ✅ Session ownership validation
- ✅ GDPR-compliant deletion

### Offline Data
- ✅ Encrypted at rest (optional)
- ✅ Local SQLite database
- ✅ No cloud backup of offline data
- ✅ User control of sync

### Search Privacy
- ✅ Private search history
- ✅ Cache stored locally
- ✅ No tracking of searches
- ✅ Autonomous decisions logged

## 📱 Frontend Integration

**Add to Layout**

```jsx
import Layout from './components/Layout';
import OfflineMode from './components/OfflineMode';
import UserProfile from './components/UserProfile';

function App() {
  return (
    <>
      <OfflineMode />
      <Layout>
        <UserProfile />
        {/* Content */}
      </Layout>
    </>
  );
}
```

## ✅ Deployment Checklist

- [ ] User sandboxing enabled
- [ ] Offline database initialized
- [ ] Search engine configured
- [ ] Web search API integrated
- [ ] Sync mechanism tested
- [ ] Encryption enabled (optional)
- [ ] Audit logging active
- [ ] GDPR deletion tested
- [ ] Performance optimized
- [ ] Documentation updated

## 🚀 Next Steps

1. Integrate real web search API
2. Add encryption to offline storage
3. Implement advanced caching strategies
4. Add user preferences UI
5. Create admin dashboard for user management
6. Set up monitoring and analytics
7. Implement backup strategies
