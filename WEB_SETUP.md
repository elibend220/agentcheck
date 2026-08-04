# 🌐 JARVIS Web Frontend - Setup Guide

Complete guide to set up and run the JARVIS AGI web application.

## 🎯 Prerequisites

### System Requirements
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher (or yarn 1.22+)
- **Modern browser**: Chrome, Firefox, Safari, or Edge (latest versions)

### Verify Installation

```bash
node --version    # Should be v16.x or higher
npm --version     # Should be v7.x or higher
```

## 📥 Installation

### 1. Navigate to Web Directory

```bash
cd agentcheck/web
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

This installs:
- React 18 for UI framework
- React Router for navigation
- Axios for HTTP requests
- Vite for fast development and building

## 🚀 Running the Application

### Development Server

```bash
npm run dev
```

Access the application at: **http://localhost:3000**

The application includes hot reload - changes to files will automatically refresh in the browser.

### Production Build

```bash
npm run build
```

Output files will be in the `dist/` directory, ready for deployment.

### Preview Production Build

```bash
npm run preview
```

Serves the production build locally to verify it works correctly.

## ⚙️ Configuration

### Backend URL Setup

By default, the app connects to `http://localhost:8000`.

**To change the backend URL:**

1. **Open Settings** (⚙️ Settings tab in app)
2. **Update API URL** field with your backend address
3. **Click Save Settings** to persist
4. **Or use preset buttons**:
   - **Local**: `http://localhost:8000`
   - **Android Emulator**: `http://10.0.2.2:8000`
   - **Local Network**: `http://192.168.x.x:8000`

### Environment Variables

Create a `.env.local` file in the `web/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
VITE_ENABLE_ANALYTICS=false
```

## 📊 Features Overview

### Chat Interface
- Real-time messaging with JARVIS
- Auto-scrolling message display
- Loading indicators for responses
- Message timestamps
- Keyboard shortcuts (Enter to send)

### Metrics Display
- **Consciousness Level**: Real-time AGI consciousness metric (0-100%)
- **Emergence Level**: System emergence and adaptation (0-100%)
- **Confidence Score**: Response confidence (0-100%)
- **Execution Time**: Backend processing time in milliseconds
- **Phases Executed**: Number of orchestrated phases used

### Session Management
- View all previous conversations
- Load any session to resume chatting
- Delete sessions with one click
- Message count tracking per session
- Automatic persistence in localStorage

### Settings
- Configure backend API URL
- Quick preset buttons for common setups
- View application information
- Keyboard shortcuts reference
- Reset to default settings

## 🎨 UI/UX Guide

### Navigation
- **💬 Chat**: Main chat interface
- **📋 Sessions**: Session history and management
- **⚙️ Settings**: Configuration and info

### Keyboard Shortcuts
- **Enter**: Send message
- **Shift + Enter**: Add new line in message
- **Tab**: Navigate between elements

### Color Indicators
- 🔷 **Blue/Cyan**: Active, primary actions
- 🟢 **Green**: Success, high metrics (80%+)
- 🟡 **Yellow**: Medium metrics (40-80%)
- 🔴 **Red**: Errors, low metrics (<40%)

## 🔗 Connecting to Backend

### Ensure Backend is Running

```bash
# Check backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### Common Connection Issues

**Error: "Failed to initialize session"**
- ✅ Backend is running on correct port
- ✅ API URL is correct in Settings
- ✅ No firewall blocking port 8000
- ✅ Network connectivity is available

**Error: "Connection refused"**
- Start backend: `cd backend && python server.py`
- Or with Docker: `docker-compose up`

**Error: "CORS error"**
- Backend CORS settings allow localhost:3000
- Check backend is listening on 0.0.0.0
- Verify no proxy/firewall blocking

## 📱 Multi-Device Access

### Access from Another Machine

1. Find your computer's local IP:
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

2. Update backend to listen on all interfaces:
```bash
# Backend listens on 0.0.0.0:8000 (default)
```

3. From other machine, use:
```
http://YOUR_IP:3000
```

## 🛠️ Troubleshooting

### Port Already in Use

**Error: "EADDRINUSE: address already in use :::3000"**

```bash
# Use different port
npm run dev -- --port 3001
```

### Dependencies Issues

**Error: "Cannot find module"**

```bash
# Clean reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

**Error: "Failed to compile"**

```bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run build
```

### Hot Reload Not Working

**Changes not appearing in browser**

```bash
# Restart dev server
npm run dev
```

### High Memory Usage

**Dev server using too much RAM**

```bash
# Restart and use production build
npm run build
npm run preview
```

## 📦 Deployment

### Docker Deployment

Create `Dockerfile` in `web/` directory:

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

Build and run:

```bash
docker build -t jarvis-web .
docker run -p 3000:3000 -e VITE_API_URL=http://backend:8000 jarvis-web
```

### Docker Compose

Add to main `docker-compose.yml`:

```yaml
services:
  jarvis-web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - jarvis-backend
    environment:
      VITE_API_URL: http://jarvis-backend:8000
    networks:
      - jarvis-network
```

### Vercel Deployment

```bash
npm install -g vercel
vercel
```

Follow prompts and set environment variable:
```
VITE_API_URL=https://api.jarvis-agi.com
```

### Netlify Deployment

```bash
npm install -g netlify-cli
netlify deploy --prod
```

Set environment variable in Netlify UI:
```
VITE_API_URL=https://api.jarvis-agi.com
```

### Static Host (S3, GCS, etc.)

```bash
npm run build
# Upload 'dist' folder to your static host
# Configure your host to serve index.html for all routes
```

## 🧪 Development Workflow

### Code Structure

```
web/src/
├── main.jsx              # App entry point
├── App.jsx               # Main component with routing
├── styles/
│   └── global.css        # Global styles and variables
├── context/
│   └── JARVISContext.jsx # Global state management
├── components/           # Reusable components
│   ├── Layout.jsx
│   ├── MessageList.jsx
│   ├── MessageInput.jsx
│   ├── MetricsDisplay.jsx
│   └── ErrorAlert.jsx
└── pages/                # Page components
    ├── ChatPage.jsx
    ├── SessionsPage.jsx
    └── SettingsPage.jsx
```

### Adding Features

1. Create component in `src/components/` or `src/pages/`
2. Use `useJARVIS()` hook for state management
3. Import global styles from `styles/global.css`
4. Use CSS modules for component-specific styles

Example:

```jsx
import { useJARVIS } from '../context/JARVISContext';
import styles from './MyComponent.module.css';

export default function MyComponent() {
  const { messages, sendMessage } = useJARVIS();
  
  return (
    <div className={styles.container}>
      {/* Component JSX */}
    </div>
  );
}
```

## 🎯 Performance Tips

### Reduce Bundle Size
```bash
npm run build
# Check size
npm run build -- --analyze
```

### Enable Gzip Compression
```bash
# nginx
gzip on;
gzip_types text/javascript application/javascript;
```

### Optimize Images
- Use WebP format
- Compress before uploading
- Use appropriate sizes

### Enable Service Worker
```bash
npm install workbox-window
# Implement in main.jsx
```

## 🔐 Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use `.env.example` for defaults
- Store secrets in deployment platform

### CORS Configuration
- Configure backend to allow origin
- Don't use `*` in production
- Specify exact domains

### Content Security Policy
- Set appropriate CSP headers
- Restrict inline scripts
- Whitelist external resources

### HTTPS
- Always use HTTPS in production
- Get SSL certificate (Let's Encrypt free)
- Redirect HTTP to HTTPS

## 📊 Monitoring

### Browser DevTools

**Console**: Check for errors
```javascript
// Clear console
console.clear()
```

**Network**: Monitor API calls
- Check response times
- Verify payload sizes
- Monitor bandwidth

**Performance**: Measure load times
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)

### Error Tracking

Add error logging:
```javascript
window.addEventListener('error', (event) => {
  console.error('Application error:', event.error);
});
```

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [React Router](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)

## ✅ Deployment Checklist

- [ ] Backend is running and accessible
- [ ] API URL is configured correctly
- [ ] All tests pass: `npm run build`
- [ ] Environment variables are set
- [ ] HTTPS is enabled (production)
- [ ] CORS is properly configured
- [ ] Error logging is enabled
- [ ] Analytics are set up (if needed)
- [ ] Database is accessible
- [ ] Backups are configured

## 🎉 Success!

Your JARVIS AGI web frontend is ready to go!

### Next Steps

1. ✅ Start dev server: `npm run dev`
2. ✅ Open http://localhost:3000
3. ✅ Configure backend URL in Settings
4. ✅ Send your first message
5. ✅ Check metrics display
6. ✅ Explore session management

**Happy chatting with JARVIS! 🚀**
