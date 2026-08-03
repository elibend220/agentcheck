# 📱 JARVIS Mobile App - Setup Guide

Complete guide to set up and run the JARVIS AGI mobile application on Android and iOS.

## 🎯 Prerequisites

### System Requirements
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher (or yarn 1.22+)
- **Java**: JDK 11+ (for Android)
- **Android SDK**: API level 24+ (for Android)
- **Xcode**: 14+ (for iOS, macOS only)

### Verify Installation

```bash
node --version    # Should be v16.x or higher
npm --version     # Should be v7.x or higher
java -version     # Should be 11+
```

## 📥 Installation Steps

### 1. Clone Repository and Navigate to Mobile Directory

```bash
cd agentcheck
cd mobile
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

This will install:
- React Native and core dependencies
- React Navigation (tabs + stack)
- GiftedChat (messaging UI)
- Axios (HTTP client)
- Vector icons (UI icons)
- AsyncStorage (local persistence)

### 3. Install Pods (iOS only)

```bash
cd ios
pod install
cd ..
```

## 🚀 Running on Android

### Setup Android Environment

1. **Install Android Studio** from https://developer.android.com/studio

2. **Set ANDROID_HOME environment variable**:

```bash
# Add to ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

3. **Reload shell**:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Start Android Emulator

**Option 1: Using Android Studio**
- Open Android Studio → AVD Manager → Create Virtual Device
- Choose device (Pixel 5 recommended)
- Choose API level 33 or higher
- Click "Play" to start emulator

**Option 2: Command line**
```bash
# List available emulators
emulator -list-avds

# Start emulator
emulator -avd <emulator_name>
```

### Run Application

```bash
# Terminal 1: Start Metro bundler
npm start

# Terminal 2: Install and run app
npm run android
```

You'll see the app launch in the emulator. If it doesn't automatically open:

```bash
# Manually run
npx react-native run-android
```

### Debug on Physical Android Device

1. **Enable USB Debugging**:
   - Go to Settings → Developer Options → USB Debugging (toggle ON)

2. **Connect device via USB**:
   ```bash
   adb devices  # Should list your device
   ```

3. **Run app**:
   ```bash
   npm run android
   ```

## 🍎 Running on iOS

### Setup iOS Environment (macOS only)

1. **Install Xcode Command Line Tools**:
```bash
xcode-select --install
```

2. **Install CocoaPods** (if not already installed):
```bash
sudo gem install cocoapods
```

3. **Update pods**:
```bash
cd ios
pod repo update
pod install
cd ..
```

### Run on iOS Simulator

```bash
# Terminal 1: Start Metro bundler
npm start

# Terminal 2: Run on iOS
npm run ios
```

The app will launch in the default iOS simulator.

### Run on Specific iOS Device

```bash
# List available simulators
xcrun simctl list devices

# Run on specific device (use from above list)
npm run ios -- --simulator "iPhone 14 Pro Max"
```

### Run on Physical iOS Device

1. **Connect device via USB**

2. **Open Xcode project**:
```bash
open ios/JARVISMobile.xcworkspace
```

3. **In Xcode**:
   - Select your physical device from the scheme dropdown
   - Click Play button to build and run

## ⚙️ Configuration

### API URL Setup

The app comes configured for Android emulator. To change the backend URL:

1. **Launch app**
2. **Go to Settings tab** (bottom right)
3. **Update API URL** field:

**For Android Emulator**:
```
http://10.0.2.2:8000
```

**For Physical Device (WiFi)**:
```
http://192.168.x.x:8000  # Use your computer's local IP
```

**For Cloud Backend**:
```
https://api.jarvis-agi.com
```

### Finding Your Computer's IP

```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
# Look for IPv4 address like 192.168.x.x
```

## 🧪 Testing the Connection

### From Android Emulator/Device

```javascript
// In a terminal, test with curl
curl -X POST http://10.0.2.2:8000/session/create

// Or from the app, go to Settings and save the API URL
// The app will show an error if connection fails
```

### Check Backend Status

```bash
# Ensure backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

## 📊 Project Structure

```
mobile/
├── App.js                    # Main application entry
├── package.json              # Dependencies
├── index.js                  # App registration
├── context/
│   └── JARVISContext.js      # Global state (messages, session, API)
├── screens/
│   ├── ChatScreen.js         # Main chat interface
│   ├── SessionsScreen.js     # Session history manager
│   └── SettingsScreen.js     # Configuration
├── components/
│   └── MetricsBar.js         # JARVIS metrics display
├── android/
│   ├── app/src/main/
│   │   └── AndroidManifest.xml
│   └── app/build.gradle
├── ios/
│   ├── Podfile
│   └── JARVISMobile.xcworkspace
├── README.md                 # Feature documentation
└── .env.example              # Configuration template
```

## 🎨 Key Features

### Chat Screen
- Real-time messaging interface
- Message history with timestamps
- Loading indicators during responses
- Automatic session initialization
- Metrics display (consciousness, emergence, confidence)
- Quick action buttons (New Session, History)

### Sessions Screen
- View all conversation sessions
- Creation dates and message counts
- Load any previous session
- Delete individual sessions
- Empty state messaging

### Settings Screen
- Configure backend API URL
- Enable/disable notifications
- Application info and version
- Feature list
- Reset to defaults option

## 🔧 Troubleshooting

### Issue: Metro Bundler Won't Start

```bash
# Clear cache and restart
npm start -- --reset-cache
```

### Issue: Module Not Found Errors

```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

### Issue: Android Build Fails

```bash
cd android
./gradlew clean
cd ..
npm run android
```

### Issue: iOS Pod Installation Fails

```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

### Issue: App Crashes on Startup

1. Check logcat (Android):
```bash
adb logcat | grep JARVISMobile
```

2. Check console (iOS):
```bash
Xcode → View → Debug Area → Console
```

### Issue: Can't Connect to Backend

1. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API URL in Settings** (should not have trailing slash)

3. **For emulator**: Use `http://10.0.2.2:8000`

4. **For physical device**: Ensure same WiFi network and use local IP

## 🚀 Development Workflow

### Hot Reload

During development, changes to JavaScript files will hot-reload:

1. Save file changes
2. Press `R` in Metro terminal (twice for full reload)
3. Or press `R` in app (Android) or Command+R (iOS)

### Debug Mode

Open React Native debugger:

```bash
# Android
adb shell input keyevent 82

# iOS
Command+D in simulator
```

Select "Debug" or "Debug Remote JS"

## 📦 Building for Release

### ⚡ Quick Build (Recommended)

Use the provided helper scripts for easy APK building:

**macOS/Linux:**
```bash
cd mobile
chmod +x build-apk.sh
./build-apk.sh
```

**Windows (PowerShell):**
```bash
cd mobile
build-apk.bat
```

The script will guide you through:
1. Checking prerequisites (Node.js, Java, Android SDK)
2. Choosing build type (Debug/Release)
3. Installing dependencies
4. Building the APK
5. Showing installation instructions

### Android APK (Manual)

```bash
cd android
./gradlew assembleRelease
cd ..
# Output: android/app/build/outputs/apk/release/app-release.apk
```

### Android App Bundle (Google Play)

```bash
cd android
./gradlew bundleRelease
cd ..
# Output: android/app/build/outputs/bundle/release/app-release.aab
```

### Installing APK on Device

**Method 1: Using ADB (easiest)**
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

**Method 2: Direct file installation**
- Copy APK to phone via USB or email
- Open file manager on phone
- Tap the APK file
- Allow installation from unknown sources (if prompted)

**Method 3: Using Android Studio**
1. Open Project
2. Build → Build Bundle(s) / APK(s) → Build APK(s)
3. Click Locate to open build folder
4. Transfer APK to phone manually

### iOS App

```bash
# Open Xcode
open ios/JARVISMobile.xcworkspace

# In Xcode:
# 1. Select Generic iOS Device
# 2. Product → Archive
# 3. Organizer window → Distribute App
# 4. Select TestFlight or App Store
```

## 📚 Additional Resources

- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs)
- [GiftedChat](https://github.com/FaridSafi/react-native-gifted-chat)
- [Axios Documentation](https://axios-http.com/)

## 🐛 Reporting Issues

If you encounter issues:

1. Check the Troubleshooting section
2. Review logs (logcat for Android, Console for iOS)
3. Verify backend connectivity: `curl http://localhost:8000/health`
4. Ensure correct API URL in Settings
5. Try clearing app data and restarting

## ✅ Next Steps

After successful installation:

1. ✅ Ensure backend server is running on port 8000
2. ✅ Configure API URL in Settings
3. ✅ Send your first message to JARVIS
4. ✅ Watch the metrics update in real-time
5. ✅ Explore session history and management

**Happy chatting with JARVIS! 🚀**
