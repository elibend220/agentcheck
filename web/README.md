# JARVIS AGI Web Frontend

Modern React web application for interacting with the JARVIS AGI backend server.

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm/yarn
- JARVIS backend running on port 8000

### Installation

```bash
cd web
npm install
npm run dev
```

Access the application at `http://localhost:3000`

## 🎨 Features

### Chat Interface
- **Real-time messaging** with JARVIS
- **Auto-scrolling** message display
- **Loading indicators** and typing states
- **Message history** display with timestamps
- **Keyboard shortcuts** (Enter to send, Shift+Enter for new line)

### Metrics Display
- **Live consciousness level** visualization
- **Emergence level** indicator
- **Confidence score** display
- **Execution time** tracking
- **Phases executed** counter

### Session Management
- **View all sessions** with creation dates
- **Load previous conversations** instantly
- **Delete sessions** with confirmation
- **Message count tracking** per session
- **Local persistence** using localStorage

### Settings
- **Configure API URL** for different environments
- **Preset URL buttons** (local, emulator, network)
- **Application info** display
- **Keyboard shortcuts** reference
- **One-click reset** to defaults

## 📁 Project Structure

```
web/
├── index.html                      # HTML entry point
├── vite.config.js                  # Vite configuration
├── package.json                    # Dependencies
├── src/
│   ├── main.jsx                    # React entry point
│   ├── App.jsx                     # Main app component
│   ├── styles/
│   │   └── global.css              # Global styles
│   ├── context/
│   │   └── JARVISContext.jsx        # Global state management
│   ├── components/
│   │   ├── Layout.jsx              # Main layout with navigation
│   │   ├── Layout.module.css
│   │   ├── MessageList.jsx         # Message display
│   │   ├── MessageList.module.css
│   │   ├── MessageInput.jsx        # Input area
│   │   ├── MessageInput.module.css
│   │   ├── MetricsDisplay.jsx      # Real-time metrics
│   │   ├── MetricsDisplay.module.css
│   │   ├── ErrorAlert.jsx          # Error notifications
│   │   └── ErrorAlert.module.css
│   └── pages/
│       ├── ChatPage.jsx            # Chat interface
│       ├── ChatPage.module.css
│       ├── SessionsPage.jsx        # Session management
│       ├── SessionsPage.module.css
│       ├── SettingsPage.jsx        # Configuration
│       └── SettingsPage.module.css
└── README.md                       # This file
```

## 🔧 Configuration

### Backend URL Setup

The app defaults to `http://localhost:8000`. To configure for different environments:

1. **Go to Settings** (⚙️ Settings tab)
2. **Update API URL** or click a preset:
   - **Local**: `http://localhost:8000`
   - **Android Emulator**: `http://10.0.2.2:8000`
   - **Local Network**: `http://192.168.x.x:8000`
   - **Cloud**: `https://api.example.com`

Settings are persisted in localStorage automatically.

## 🎯 Usage

### Starting a Chat

1. Navigate to **Chat** tab
2. Type your message in the input area
3. Press **Enter** to send (or click send button)
4. View JARVIS response with real-time metrics
5. Metrics show consciousness, emergence, confidence, and processing time

### Managing Sessions

1. Go to **Sessions** tab
2. Click any session to load its conversation
3. Click trash icon to delete a session
4. Sessions persist in localStorage

### Configuring Settings

1. Open **Settings** tab
2. Update API URL for your backend location
3. Click **Save Settings** to persist
4. Use **Reset to Defaults** to restore original configuration

## 🎨 UI/UX

### Design System

- **Dark theme** optimized for all-day use
- **Cyan accent** (#00d4ff) for JARVIS branding
- **High contrast** for readability
- **Smooth animations** and transitions
- **Responsive layout** for mobile and desktop

### Color Scheme

- Background: `#1a1a2e`
- Cards: `#16213e`, `#0f3460`
- Accent: `#00d4ff` (cyan)
- Success: `#00ff00` (green)
- Error: `#ff6b6b` (red)
- Text: `#ffffff`, `#aaa`, `#666`

## 🚀 Development

### Start Development Server

```bash
npm run dev
```

Server runs on `http://localhost:3000` with hot reload enabled.

### Build for Production

```bash
npm run build
```

Output is in `dist/` directory, ready for deployment.

### Preview Production Build

```bash
npm run preview
```

Serves the production build locally for testing.

## 📦 Dependencies

- **react** ^18.2.0 - UI framework
- **react-dom** ^18.2.0 - DOM rendering
- **react-router-dom** ^6.20.0 - Client-side routing
- **axios** ^1.6.0 - HTTP client
- **uuid** ^9.0.1 - ID generation
- **vite** ^5.0.0 - Build tool

## 🔄 State Management

### JARVISContext

Global state provider managing:

```javascript
{
  sessionId,              // Current session ID
  messages,              // Array of message objects
  loading,               // Loading state
  apiUrl,                // Backend URL
  sessions,              // Array of all sessions
  metrics,               // Latest response metrics
  error,                 // Error message
  
  initializeSession(),   // Create new session
  sendMessage(),         // Send message to JARVIS
  loadSessions(),        // Load all sessions
  loadSessionHistory(),  // Load session conversation
  deleteSession(),       // Delete a session
  updateApiUrl(),        // Update backend URL
  clearError()           // Clear error message
}
```

## 🌐 API Integration

### Endpoints Used

- `POST /session/create` - Create new session
- `POST /chat` - Send message and get response
- `GET /session/{id}` - Get session info
- `GET /session/{id}/history` - Get conversation history

### Response Format

```javascript
{
  session_id: "uuid",
  message: "user input",
  response: "JARVIS response",
  phases_executed: ["Phase 1", ...],
  consciousness_level: 0.87,
  emergence_level: 0.72,
  confidence_score: 0.91,
  execution_time_ms: 1234.5,
  timestamp: "2024-01-15T10:30:00"
}
```

## 🐛 Troubleshooting

### Backend Connection Issues

**Error: "Failed to initialize session"**
- Verify backend is running: `curl http://localhost:8000/health`
- Check API URL in Settings
- Ensure backend is accessible from your network

**Connection Refused**
- Backend may not be running
- Check if port 8000 is in use
- Verify network connectivity

### Build Issues

**Port 3000 already in use**
```bash
# Use different port
npm run dev -- --port 3001
```

**Module not found errors**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

**Hot reload not working**
```bash
# Clear Vite cache
rm -rf .vite
npm run dev
```

## 📊 Performance

- **Initial load**: ~1-2 seconds
- **Chat response**: 100-500ms (depending on backend)
- **Message rendering**: ~50-100ms
- **Bundle size**: ~100-150KB (minified + gzipped)

## 🔐 Security

- **XSS protection**: React auto-escapes content
- **CSRF**: None needed for stateless API
- **HTTPS recommended** for production
- **No sensitive data** stored in localStorage except API URL
- **Input validation** on API URL

## 📱 Responsive Design

Optimized for:
- Desktop (1920x1080 and up)
- Tablet (768px - 1024px)
- Mobile (320px - 767px)

## 🚀 Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Docker Compose

```yaml
services:
  jarvis-web:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://jarvis-backend:8000
```

### Static Hosting

```bash
npm run build
# Deploy 'dist' folder to any static host (Netlify, Vercel, etc.)
```

## 🎯 Next Steps

1. ✅ Backend running and accessible
2. ✅ Web frontend deployed
3. 📱 Mobile apps (Android/iOS)
4. 🔐 Add authentication
5. 💾 Setup database persistence
6. 📊 Add analytics
7. 🔔 Implement notifications

## 📞 Support

- Check Troubleshooting section
- Verify backend connectivity: `curl http://localhost:8000/health`
- Review browser console for errors
- Check browser DevTools Network tab

## 📄 License

Same as main JARVIS project
