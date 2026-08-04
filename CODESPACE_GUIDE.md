# 🚀 GitHub Codespace Guide for JARVIS AGI

Use GitHub Codespace to develop and build JARVIS AGI entirely in your browser!

## ✨ What You Get

- ☁️ Full development environment in the browser
- 📱 Build Android APK with EAS Build
- 🔧 Backend server running
- 🌐 Web frontend development
- 🔗 All ports forwarded automatically
- 💾 Changes synced to GitHub

## 🎯 Quick Start (5 minutes)

### 1. Create Codespace

On GitHub:
```
repository → Code → Codespaces → Create codespace on main
```

Or click: https://github.com/codespaces/new?repo=elibend220/agentcheck

### 2. Wait for Setup

The Codespace will:
- ✅ Install Node.js, Python, Java
- ✅ Install all project dependencies
- ✅ Install EAS CLI
- ✅ Show setup complete message

**Takes ~3-5 minutes first time**

### 3. Build APK

In Codespace terminal:

```bash
cd mobile
eas login
# Paste your Expo token from: https://expo.dev/settings/account-security
# (Create free account if needed)

eas build --platform android
```

**Wait 5-10 minutes, then download APK!**

## 🔧 What's Installed

- **Node.js 18** - JavaScript runtime
- **Python 3.11** - Backend development
- **Java 11** - Build tools
- **Git** - Version control
- **EAS CLI** - Cloud APK builder
- **VS Code Extensions**:
  - TypeScript support
  - Python linting
  - ESLint / Prettier
  - Live Server

## 📂 Folder Structure in Codespace

```
/workspaces/agentcheck/
├── mobile/           # React Native app
├── backend/          # FastAPI server
├── web/              # React web app
├── .devcontainer/    # Codespace config
└── ... (other files)
```

## 💻 Common Tasks

### Task 1: Build Android APK

```bash
cd mobile
eas login
eas build --platform android
# Download when ready
```

### Task 2: Run Backend Server

```bash
cd backend
python server.py
# Server at: http://localhost:8000
```

### Task 3: Run Web Frontend

```bash
cd web
npm install
npm run dev
# App at: http://localhost:5173
```

### Task 4: Run Mobile Dev Server

```bash
cd mobile
npm start
# Will show QR code for Expo Go
```

## 🔗 Port Forwarding

Codespace automatically forwards:

| Port | Service | URL |
|------|---------|-----|
| 8000 | Backend | `https://codespace-url-8000...` |
| 3000 | Dev | `https://codespace-url-3000...` |
| 5173 | Web | `https://codespace-url-5173...` |

**Share URLs with others** - they can access your running servers!

## 📱 Building APK Step by Step

```bash
# 1. Open terminal in Codespace
# (Terminal → New Terminal)

# 2. Navigate to mobile directory
cd mobile

# 3. Login to Expo (one-time)
eas login
# Paste token from: https://expo.dev/settings/account-security

# 4. Build APK
eas build --platform android

# 5. Choose options:
# - Build profile: production (or preview for debug)
# - Build type: apk
# - Name: jarvis-v1.0 (any name)

# 6. Wait for build to complete
# - You'll see progress in terminal
# - Build URL: https://expo.dev/accounts/.../builds/...

# 7. Download APK
# - Click "Download APK" on build page
# - Or run: eas build:download <build-id>

# 8. Transfer to phone
# - Copy APK to phone via USB
# - Or email it to yourself
# - Install: tap file → Allow installation
```

## ⚙️ Configuration

### Change Backend URL in Mobile App

1. In Codespace, go to: `mobile/context/JARVISContext.jsx`
2. Find: `API_URL`
3. Change to your Codespace URL or remote backend
4. Save (auto-sync to GitHub)

### Backend Settings

1. Go to: `backend/server.py`
2. Modify configuration as needed
3. Restart server

## 🐛 Troubleshooting

### "eas login failed"

```bash
# Try again with explicit logout
eas logout
eas login
# Paste token carefully
```

### "Build won't start"

```bash
# Check your Expo account has credits
# (Free tier is usually enough)

# Or try preview build (debug):
eas build --platform android --profile preview
```

### "Port already in use"

Codespace auto-manages ports, but if needed:
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Restart service
python server.py
```

### "Changes not syncing to GitHub"

```bash
# Codespace auto-syncs, but manually sync if needed:
git add -A
git commit -m "Your message"
git push origin main
```

## 💡 Tips & Tricks

- **Split terminals:** Right-click terminal tab → Split
- **Open ports panel:** Click "Ports" tab (shows forwarded URLs)
- **Download files:** Right-click in Explorer → Download
- **Share Codespace:** Click "Code" → "Codespaces" → "..." → Share
- **Rebuild Codespace:** Click "..." → Rebuild container (if setup breaks)

## 🎯 Complete Workflow

```bash
# Terminal 1: Start Backend
cd backend
python server.py
# Runs on http://localhost:8000

# Terminal 2: Start Web Frontend
cd web
npm run dev
# Runs on http://localhost:5173

# Terminal 3: Build APK
cd mobile
eas login
eas build --platform android
# Build in Expo cloud

# Terminal 4: Monitor (optional)
cd mobile
npm start
# Starts Metro bundler for live testing
```

## 📚 Resources

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [VS Code in Browser](https://code.visualstudio.com/docs/remote/codespaces)
- [Expo Build Docs](https://docs.expo.dev/build/introduction/)
- [JARVIS AGI Docs](README.md)

## ✅ Done!

Your development environment is ready. Start building! 🚀

---

**Questions?** Check other guides in the repo:
- [QUICK_EAS_BUILD.md](mobile/QUICK_EAS_BUILD.md) - EAS Build quick start
- [EAS_BUILD_GUIDE.md](EAS_BUILD_GUIDE.md) - Detailed EAS guide
- [BACKEND_QUICKSTART.md](BACKEND_QUICKSTART.md) - Backend setup
- [WEB_SETUP.md](WEB_SETUP.md) - Web frontend setup
