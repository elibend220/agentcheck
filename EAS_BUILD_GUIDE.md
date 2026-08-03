# ☁️ EAS Build - Cloud APK Builder for JARVIS AGI

**EAS Build** is Expo's cloud build service that builds your Android APK without needing a local Android SDK setup.

## ✅ What You Need

1. **Expo Account** (free) - https://expo.dev
2. **eas-cli** installed - `npm install -g eas-cli`
3. **Git** installed on your computer

## 🚀 Getting Started (5 minutes)

### Step 1: Create Expo Account

1. Go to https://expo.dev/signup
2. Sign up with email (or Google/GitHub)
3. Confirm your email
4. Go to https://expo.dev/settings/account-security
5. Create a new token (name: "jarvis-build")
6. Copy the token (you'll use it once)

### Step 2: Login to EAS CLI

```bash
cd mobile
eas login
# Paste your token from Step 1
```

### Step 3: Build APK

```bash
eas build --platform android
```

**Choose options when prompted:**
- Build type: **release** (for final APK)
- Use credentials stored in Expo?: **No** (simpler)

### Step 4: Wait & Download

- EAS will build in the cloud (~5-10 minutes)
- You'll see a progress link like: `https://expo.dev/accounts/.../builds/...`
- Download the `.apk` file when ready
- Install on your phone with: `adb install downloaded.apk`

## 🔑 Alternative: Using Environment Variables (CI/Automation)

If you want to automate builds without interactive login:

```bash
# 1. Export your token
export EXPO_TOKEN="your_token_here"

# 2. Build without login
eas build --platform android --non-interactive

# 3. APK URL will be printed to console
```

## 📁 Project Files Already Set Up

The following files have been configured for you:

**app.json** - Expo configuration
```json
{
  "expo": {
    "name": "JARVIS AGI",
    "slug": "jarvis-agi",
    "version": "1.0.0",
    "android": {
      "package": "com.jarvis.mobile"
    }
  }
}
```

**eas.json** - Build configuration
```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "apk"
      }
    }
  }
}
```

**package.json** - Updated with Expo dependencies

## 🎯 Complete Workflow

```bash
# 1. Navigate to project
cd agentcheck/mobile

# 2. Login (one time)
eas login

# 3. Build APK
eas build --platform android

# 4. Wait for build to complete (~5-10 minutes)
# You'll see progress in terminal and browser

# 5. Download APK from the provided link
# Or check: https://expo.dev/accounts/yourname/builds

# 6. Install on phone
adb install app-production.apk

# 7. Configure in app
# Open JARVIS AGI → Settings → Set API URL
# (http://192.168.1.X:8000 or your backend URL)

# 8. Ensure backend is running
cd ../backend
python server.py
```

## 📋 Build Options

### Debug Build (Faster, for testing)
```bash
eas build --platform android --profile preview
```

### Release Build (Production, signed)
```bash
eas build --platform android --profile production
```

### Check Build Status
```bash
eas build:list
```

### Download Previous Build
```bash
eas build:download <build-id>
```

## 🐛 Troubleshooting

### Error: "User is not authenticated"
```bash
eas logout
eas login
# Follow prompts to login again
```

### Error: "app.json not found"
```bash
# Make sure you're in the mobile directory
cd mobile
eas build --platform android
```

### Build fails with "Gradle error"
- Check that package.json has valid syntax
- Try clearing cache: `npm cache clean --force`
- Run: `npm install` again

### Long build times
- EAS can be slower than local builds (5-15 minutes)
- This is normal - wait for completion
- You can check progress on https://expo.dev

## 🔐 Security Notes

- ✅ EAS handles signing automatically
- ✅ Your token is only used for authentication
- ✅ APK is built in Expo's secure servers
- ✅ Download link expires after 30 days

## 📱 After Installing APK

1. **Open JARVIS AGI** on your phone
2. **Go to Settings** (tab at bottom)
3. **Enter API URL:**
   - Local network: `http://192.168.1.X:8000`
   - Replace X with your computer's IP
4. **Ensure Backend is running:**
   ```bash
   cd backend
   python server.py
   ```

## 💡 Tips

- **Faster testing:** Use `eas build --profile preview` for debug APK
- **Multiple builds:** You can run multiple builds in parallel
- **View build logs:** Click the build link to see full logs
- **Skip login:** Use `EXPO_TOKEN` environment variable for automation

## 🎉 That's It!

EAS Build handles all the complexity of Android builds. No Android SDK needed!

---

**Questions?** Visit https://docs.expo.dev/build/introduction/
