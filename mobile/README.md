# JARVIS AGI Mobile Application

React Native mobile application for iOS and Android that connects to the JARVIS AGI backend server.

## ⚡ Build APK Instantly (Recommended)

Use **EAS Build** to build your APK in the cloud with no local setup:

1. **Create free Expo account** → https://expo.dev
2. **Login:** `eas login`
3. **Build:** `eas build --platform android`
4. **Download** when ready (~5-10 minutes)
5. **Install:** `adb install app.apk`

📖 **See [QUICK_EAS_BUILD.md](QUICK_EAS_BUILD.md)** for step-by-step instructions in Hebrew

Or check [EAS_BUILD_GUIDE.md](../EAS_BUILD_GUIDE.md) for detailed guide.

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Node.js 16+ and npm/yarn
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development on macOS)

### Installation

```bash
# Install dependencies
npm install
# or
yarn install

# For React Native vector icons
npx react-native-asset-link
```

### Running on Android

```bash
# Start Metro bundler
npm start

# In another terminal, run on Android emulator or device
npm run android

# Or with specific device
adb devices  # List connected devices
npx react-native run-android --deviceId <device-id>
```

### Running on iOS

```bash
# Install pod dependencies (first time only)
cd ios
pod install
cd ..

# Start Metro bundler
npm start

# In another terminal, run on iOS simulator
npm run ios
```

## 📱 Features

### Chat Interface
- **Real-time messaging** with JARVIS AGI backend
- **Message history** display with timestamps
- **Session management** to organize conversations
- **Auto-scroll** to latest messages
- **Typing indicators** and loading states

### Metrics Display
- **Consciousness Level** - Real-time AGI consciousness metric
- **Emergence Level** - System emergence and adaptation level
- **Confidence Score** - Response confidence metric
- **Execution Time** - Processing time in milliseconds
- **Phases Executed** - Number of orchestrated phases used

### Session Management
- **View all sessions** with creation dates and message counts
- **Load session history** to resume previous conversations
- **Delete sessions** to manage storage
- **Unique session IDs** for tracking

### Settings
- **Configure API URL** for local, WiFi, or cloud backends
- **Manage preferences** (notifications, dark mode)
- **View application info** and feature list
- **Reset to defaults** option

## 🔧 Configuration

### API URL Setup

The app defaults to Android emulator:
```
http://10.0.2.2:8000
```

For different environments, update in Settings screen:

**Android Emulator:**
```
http://10.0.2.2:8000
```

**Physical Device (Local WiFi):**
```
http://192.168.x.x:8000
```

**Cloud Backend:**
```
https://api.jarvis-agi.com
```

### Environment-specific Setup

Create `.env` file in project root:
```env
API_URL=http://10.0.2.2:8000
ENABLE_LOGGING=true
DEBUG_MODE=false
```

## 📁 Project Structure

```
mobile/
├── App.js                          # Main app entry point
├── package.json                    # Dependencies
├── context/
│   └── JARVISContext.js           # Global state management
├── screens/
│   ├── ChatScreen.js              # Main chat interface
│   ├── SessionsScreen.js          # Session history
│   └── SettingsScreen.js          # Configuration
├── components/
│   └── MetricsBar.js              # JARVIS metrics display
└── README.md                       # This file
```

## 🎨 UI/UX

### Theme
- **Dark mode** optimized for nighttime use
- **Cyan accent color** (#00d4ff) for JARVIS branding
- **High contrast** for readability
- **Smooth animations** and transitions

### Navigation
- **Bottom tab navigation** for easy access to Chat, Sessions, and Settings
- **Stack navigation** for detailed views
- **Gesture-based** navigation on iOS

## 🔄 API Integration

### Session Lifecycle

```javascript
// 1. Initialize session (automatic)
const sessionId = await initializeSession();

// 2. Send message
await sendMessage("Hello JARVIS");

// 3. Receive response with metrics
// Response includes consciousness_level, emergence_level, etc.

// 4. View history
await loadSessionHistory(sessionId);

// 5. Delete session when done
await deleteSession(sessionId);
```

### API Endpoints Used

- `POST /session/create` - Create new session
- `POST /chat` - Send message and get response
- `GET /session/{id}/history` - Get conversation history
- `GET /session/{id}` - Get session info

## 🔐 Security Considerations

- API URLs stored in AsyncStorage (not encrypted in dev)
- Session IDs generated server-side (UUID v4)
- No authentication required (add JWT in production)
- HTTPS recommended for production

## 📊 State Management

Uses React Context API with `JARVISContext`:

```javascript
const { 
  messages,           // Current messages array
  sessionId,         // Current session ID
  loading,           // Loading state
  metrics,           // Last response metrics
  sendMessage,       // Send message function
  initializeSession, // Create new session
  loadSessionHistory // Load previous conversation
} = useJARVIS();
```

## 🐛 Troubleshooting

### Connection Issues

**Error: "Failed to initialize session"**
- Check API URL in Settings
- Ensure backend server is running
- For emulator, use `http://10.0.2.2:8000`
- For device, ensure on same WiFi network

**WebSocket Connection Refused**
- Verify backend is running: `curl http://localhost:8000/health`
- Check firewall settings
- Ensure port 8000 is accessible

### Build Issues

**Metro Bundler Errors**
```bash
npm start -- --reset-cache
```

**Pod Installation Failed (iOS)**
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

**Android Gradle Errors**
```bash
cd android
./gradlew clean
cd ..
npm run android
```

## 📈 Performance

- **Average response time**: 100-500ms
- **Session limit**: 1000 concurrent sessions
- **Message history**: Stored locally in AsyncStorage
- **Memory usage**: ~50-100MB for normal operation

## 🚀 Building for Release

### Android

```bash
# Build APK
cd android
./gradlew assembleRelease
cd ..
# APK: android/app/build/outputs/apk/release/app-release.apk

# Build AAB (Google Play)
cd android
./gradlew bundleRelease
cd ..
```

### iOS

```bash
# Build for TestFlight/App Store
xcode-select --install
cd ios
pod install
cd ..
# Open in Xcode:
open ios/jarvisMobile.xcworkspace
# Then: Product > Archive
```

## 📝 Dependencies

- **react-native-gifted-chat** - Chat UI component
- **@react-navigation** - Navigation framework
- **axios** - HTTP client
- **uuid** - Unique ID generation
- **@react-native-async-storage** - Local storage

## 🔄 Updates & Maintenance

### Check for Updates
```bash
npm outdated
npm update
```

### Upgrade React Native
```bash
npx react-native upgrade
```

## 📞 Support

For issues or questions:
1. Check Troubleshooting section
2. Review backend logs: `docker-compose logs -f`
3. Verify API connectivity: `curl http://localhost:8000/health`

## 📄 License

Same as main JARVIS project
