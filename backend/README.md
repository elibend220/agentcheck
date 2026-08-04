# JARVIS AGI Backend Server

RESTful API backend for the JARVIS AGI system with WebSocket support for real-time communication.

## 🚀 Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

Server will be available at: `http://localhost:8000`

### Docker

```bash
# Build and run with Docker Compose
docker-compose up

# Build only
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop server
docker-compose down
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### System Status
- `GET /` - Root endpoint with API info
- `GET /status` - System status
- `GET /health` - Health check

### Sessions
- `POST /session/create` - Create new session
- `GET /session/{session_id}` - Get session info
- `GET /session/{session_id}/history` - Get conversation history

### Chat
- `POST /chat` - Send message and get response
- `WebSocket /ws/{session_id}` - Real-time WebSocket chat

## 💬 Usage Examples

### REST API Chat

```bash
# Create a session
curl -X POST http://localhost:8000/session/create

# Send a message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "What is consciousness?"
  }'
```

### WebSocket Chat (JavaScript)

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/session-id-here');

// Connection established
ws.onopen = () => {
  console.log('Connected to JARVIS');
  
  // Send message
  ws.send(JSON.stringify({
    message: "Hello JARVIS!"
  }));
};

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data);
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Python Client

```python
import requests
import json

# Create session
session_response = requests.post('http://localhost:8000/session/create')
session_id = session_response.json()['session_id']

# Send message
chat_response = requests.post(
    'http://localhost:8000/chat',
    json={
        'session_id': session_id,
        'message': 'What are your capabilities?'
    }
)

result = chat_response.json()
print(f"Response: {result['response']}")
print(f"Consciousness Level: {result['consciousness_level']:.0%}")
print(f"Emergence Level: {result['emergence_level']:.0%}")
print(f"Execution Time: {result['execution_time_ms']:.1f}ms")
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:
- `HOST` / `PORT` - Server address
- `ENABLE_PHASE*` - Which phases to enable
- `LLM_PROVIDER` - LLM service (openai, anthropic, etc.)
- `LOG_LEVEL` - Logging verbosity

## 🧠 Phases Explanation

The backend orchestrates all 23 phases of the JARVIS system:

- **Phases 1-3**: NLP, Knowledge, Consciousness
- **Phases 4-5**: Tool Selection & Quantum Optimization
- **Phases 6-8**: Learning, Memory, Error Recovery
- **Phases 9-10**: Explainability, Planning
- **Phases 11-13**: Personal Assistant, Multi-channel, Plugins
- **Phases 14-15**: Real-time Streaming, Emotional Intelligence
- **Phases 16-18**: System Engineering, Constitutional, Safety
- **Phases 19-20**: Personality, Risk Assessment
- **Phases 21-22**: Voice, System Integration
- **Phase 23**: Consciousness Evolution & Transcendence

## 📊 Response Format

All chat responses include:

```json
{
  "session_id": "uuid",
  "message": "User input",
  "response": "JARVIS response text",
  "phases_executed": ["Phase 1", "Phase 2", ...],
  "consciousness_level": 0.87,
  "emergence_level": 0.72,
  "confidence_score": 0.91,
  "execution_time_ms": 1234.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔐 Security

- CORS enabled for cross-origin requests
- WebSocket connections per session
- Input validation with Pydantic
- Error handling and logging
- Optional authentication (configure in .env)

## 📝 Logging

Logs are output to console with timestamps:

```
2024-01-15 10:30:00 INFO: Session created: abc123...
2024-01-15 10:30:01 INFO: Message received from user
2024-01-15 10:30:02 INFO: Processing complete - 5 phases executed
```

## 🚨 Troubleshooting

### Port 8000 already in use
```bash
# Change port in .env or use different port
docker-compose up -p 8001:8000
```

### WebSocket connection refused
- Ensure server is running: `GET http://localhost:8000/health`
- Check firewall settings
- Verify session ID is valid

### High memory usage
- Reduce `MAX_SESSIONS` in .env
- Enable session timeout
- Restart server to clear inactive sessions

## 📈 Performance

- Average response time: 100-500ms (depending on phases)
- Max concurrent WebSocket connections: 1000+
- Database-ready (PostgreSQL support)

## 🔄 Integration with Frontend

The backend is designed to work with:
- React/Vue.js web applications
- React Native mobile apps
- Flutter mobile apps
- Native Android/iOS apps

## 📦 Deployment

### Production Checklist

- [ ] Configure real LLM API (OpenAI/Anthropic)
- [ ] Set `DEBUG=false` in .env
- [ ] Configure database (PostgreSQL)
- [ ] Enable authentication
- [ ] Set up monitoring/logging
- [ ] Configure CORS origins properly
- [ ] Use HTTPS/WSS in production
- [ ] Set up rate limiting
- [ ] Configure backup strategy

### Heroku Deployment

```bash
# Create Procfile
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create
heroku config:set PYTHONUNBUFFERED=1
git push heroku main
```

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs: `docker-compose logs -f`
3. Open issue on GitHub

## 📄 License

Same as main JARVIS project
