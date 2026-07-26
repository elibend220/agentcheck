# Frontend Architecture: React Dashboard

## Overview

**Separation of Concerns**: Complete decoupling between trading engine (Backend) and user interface (Frontend)

```
┌─────────────────────────────────────────────────────────┐
│                    React Dashboard (Port 3000)          │
├─────────────────────────────────────────────────────────┤
│ - Real-time market data display                        │
│ - Position management interface                        │
│ - Performance charts & analytics                       │
│ - Trading controls (start/stop)                        │
│ - Alert notifications                                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ REST API + WebSocket
                   │ (HTTP/WS)
                   ↓
┌─────────────────────────────────────────────────────────┐
│               Backend API Server (Port 8000)            │
├─────────────────────────────────────────────────────────┤
│ - FastAPI (Python)                                     │
│ - Trading Engine Integration                          │
│ - Real-time data endpoints                            │
│ - WebSocket for live updates                          │
└─────────────────────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│            Trading Engine (Python/Julia)               │
├─────────────────────────────────────────────────────────┤
│ - Scalping Engine                                      │
│ - Risk Management                                      │
│ - Order Flow Analysis                                  │
│ - Bifurcated Architecture (Ring Buffer + Worker)      │
└─────────────────────────────────────────────────────────┘
```

## Frontend Structure

### Directory Layout

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js              # API client & WebSocket
│   ├── components/
│   │   ├── Dashboard.jsx          # Main dashboard
│   │   ├── Dashboard.css
│   │   ├── StatusPanel.jsx        # Trading status
│   │   ├── StatusPanel.css
│   │   ├── PositionsPanel.jsx     # Open positions
│   │   ├── PositionsPanel.css
│   │   ├── ControlPanel.jsx       # Start/Stop controls
│   │   ├── ControlPanel.css
│   │   ├── MarketStatePanel.jsx   # Market session info
│   │   ├── MarketStatePanel.css
│   │   ├── AlertsPanel.jsx        # System alerts
│   │   ├── AlertsPanel.css
│   │   ├── PerformanceChart.jsx   # P&L chart
│   │   └── PerformanceChart.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── .env                           # Environment variables
```

## Key Technologies

### Core
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Axios** - HTTP client
- **WebSocket API** - Real-time updates

### UI/UX
- **Tailwind CSS** - Utility CSS framework
- **Lucide React** - Icons
- **Recharts** - Data visualization

### Styling Approach
- **CSS Modules** - Component-scoped styles
- **CSS Variables** - Theme management
- **Dark Theme** - Production-optimized colors

## Component Architecture

### Dashboard (Main Container)
```jsx
<Dashboard>
  ├── StatusPanel           // Current trading status
  ├── PositionsPanel        // Open positions
  ├── ControlPanel          // Start/Stop trading
  ├── MarketStatePanel      // Market session info
  ├── PerformanceChart      // P&L visualization
  └── AlertsPanel           // System alerts
</Dashboard>
```

### Data Flow

```
1. Component Mount
   ↓
2. useEffect(() => {
     fetchData()  // Get initial state from API
     connectWebSocket()  // Listen for real-time updates
     setInterval(pollData, 2000)  // Backup polling
   })
   ↓
3. State Update
   setState(data)
   ↓
4. Component Render
   Reflect latest state in UI
```

### API Integration

**REST Endpoints (Polling)**:
```
GET  /health                    # Health check
GET  /api/status               # Current status
GET  /api/market-state         # Market info
GET  /api/risk-parameters      # Risk config
GET  /api/performance          # Performance metrics
GET  /api/positions            # Open positions
GET  /api/alerts               # Recent alerts
GET  /api/diagnostics          # System diagnostics
POST /api/start                # Start trading
POST /api/stop                 # Stop trading
```

**WebSocket (Real-time)**:
```
WS   /ws/market-updates        # Live updates
     Sends: Status updates every 1 second
```

### API Client

```javascript
// file: api/client.js

import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})

// All endpoints in one place
export const tradingAPI = {
  getStatus: () => apiClient.get('/api/status'),
  getPositions: () => apiClient.get('/api/positions'),
  startTrading: () => apiClient.post('/api/start'),
  // ... more endpoints
}

// WebSocket connection
export class TradingWebSocket {
  connect() { /* ... */ }
  send(data) { /* ... */ }
  disconnect() { /* ... */ }
}
```

## Real-Time Updates Strategy

### Dual Approach

1. **WebSocket** (Preferred)
   - Live data push from server
   - Sub-100ms latency
   - Fallback to polling if disconnected

2. **Polling** (Fallback)
   - Every 2 seconds HTTP GET
   - Covers network interruptions
   - Ensures UI freshness

```javascript
// Connect WebSocket
const ws = new TradingWebSocket(
  (data) => setStatus(data),  // onMessage
  (error) => setError(error), // onError
  () => setWsConnected(false) // onClose
)
ws.connect()

// Fallback polling
setInterval(async () => {
  const data = await tradingAPI.getStatus()
  setStatus(data)
}, 2000)
```

## State Management

### Per-Component State

```javascript
const Dashboard = () => {
  const [status, setStatus] = useState(null)
  const [positions, setPositions] = useState([])
  const [performance, setPerformance] = useState(null)
  const [marketState, setMarketState] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [wsConnected, setWsConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
}
```

### No Global State Manager Needed
- Simple, single-source updates from API
- React Context/Redux would be overkill
- All data flows from backend

## Styling System

### Design System

```css
:root {
  /* Colors */
  --primary: #3b82f6    /* Blue */
  --success: #10b981    /* Green */
  --warning: #f59e0b    /* Amber */
  --danger: #ef4444     /* Red */
  --info: #06b6d4       /* Cyan */

  /* Dark Theme (Production) */
  --bg-primary: #0f172a
  --bg-secondary: #1e293b
  --bg-tertiary: #334155
  --text-primary: #f1f5f9
  --text-secondary: #cbd5e1
}
```

### Component Styles
- Each component has scoped `.css` file
- Reusable classes (`panel`, `metric`, `warning-box`)
- Mobile-responsive grid system
- Smooth transitions & animations

## Responsive Design

### Breakpoints

```css
Desktop     (> 1400px) → 3 columns
Tablet      (768-1400px) → 2 columns
Mobile      (< 768px) → 1 column
```

### Grid Layout

```javascript
// Dashboard grid adapts to screen size
<div className="dashboard-grid">
  {/* Automatically reflows */}
</div>
```

## Performance Optimizations

### 1. Lazy Updates
```javascript
// Only update if data actually changed
if (JSON.stringify(newStatus) !== JSON.stringify(status)) {
  setStatus(newStatus)
}
```

### 2. Debounced WebSocket
```javascript
// Limit update frequency
const debouncedUpdate = useCallback(
  debounce(setStatus, 100),
  []
)
```

### 3. Chart Optimization
```javascript
// Recharts with animation disabled
<Area isAnimationActive={false} />
```

## Development Workflow

### Setup

```bash
cd frontend
npm install
npm run dev        # Start dev server (port 3000)
npm run build      # Production build
npm run preview    # Preview build
```

### Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Hot Module Replacement
- Vite supports instant HMR
- Changes reflect in browser immediately
- No page refresh needed

## Error Handling

### Network Errors
```javascript
catch (err) {
  setError(err.message)
  // Show error UI to user
  // Auto-retry on reconnect
}
```

### WebSocket Reconnection
```javascript
// Exponential backoff
attemptReconnect() {
  const delay = Math.pow(2, attempts) * 1000
  setTimeout(() => this.connect(), delay)
}
```

## Security Considerations

### CORS
```javascript
// Backend allows frontend origin
CORSMiddleware(
  allow_origins=["http://localhost:3000"],
  allow_credentials=True
)
```

### Authentication (Future)
```javascript
// Store token in localStorage
const token = localStorage.getItem('authToken')
apiClient.defaults.headers.Authorization = `Bearer ${token}`
```

### HTTPS (Production)
- All API calls should use HTTPS
- WebSocket should use WSS

## Testing Strategy

### Unit Tests
```javascript
// Test individual components
import { render, screen } from '@testing-library/react'
test('StatusPanel displays capital correctly', () => {
  render(<StatusPanel status={mockStatus} />)
  expect(screen.getByText('$10000.00')).toBeInTheDocument()
})
```

### Integration Tests
```javascript
// Test API integration
test('Dashboard fetches and displays status', async () => {
  render(<Dashboard />)
  await waitFor(() => expect(screen.getByText('Trading Status')))
})
```

### E2E Tests
```javascript
// Test full workflow
describe('Trading Dashboard E2E', () => {
  test('User can start/stop trading', async () => {
    // Complete user journey
  })
})
```

## Deployment

### Production Build

```bash
npm run build
# Creates optimized build in ./dist
```

### Serve Production Build

```bash
npm run preview
# Tests production build locally
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY src ./src
COPY public ./public
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

### Phase 2: Advanced Features
- [ ] Multi-symbol support
- [ ] Custom dashboard layouts
- [ ] Dark/Light theme toggle
- [ ] Historical trade analysis
- [ ] Risk heat maps
- [ ] Performance attribution

### Phase 3: Mobile App
- [ ] React Native mobile app
- [ ] Push notifications
- [ ] Biometric auth
- [ ] Offline mode

### Phase 4: AI Integration
- [ ] Natural language queries
- [ ] ML-powered recommendations
- [ ] Anomaly detection alerts
- [ ] Predictive analytics

---

**Architecture Summary**:
- ✅ Clear separation: Frontend (React) ↔ Backend (FastAPI)
- ✅ RESTful + WebSocket for real-time data
- ✅ Modern UI/UX with responsive design
- ✅ Production-ready performance optimizations
- ✅ Comprehensive error handling & reconnection logic
- ✅ Easily extensible for future features

**Status**: Ready for Phase 2 Development
