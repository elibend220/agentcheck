#!/bin/bash

# 🚀 JARVIS AGI - Automated APK Builder
# Usage: ./build-apk-automated.sh YOUR_EXPO_TOKEN

echo "╔════════════════════════════════════════════════════════╗"
echo "║          JARVIS AGI - Automated APK Builder             ║"
echo "║              (Powered by EAS Build)                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if token provided
if [ -z "$1" ]; then
    echo "❌ Error: Expo token required"
    echo ""
    echo "Usage: ./build-apk-automated.sh YOUR_EXPO_TOKEN"
    echo ""
    echo "To get your token:"
    echo "1. Go to: https://expo.dev/settings/account-security"
    echo "2. Create token (or copy existing one)"
    echo "3. Run: ./build-apk-automated.sh <paste-token-here>"
    echo ""
    exit 1
fi

EXPO_TOKEN="$1"

# Verify we're in mobile directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "Make sure you're in the mobile directory"
    exit 1
fi

echo "✅ Expo token received"
echo "📦 Installing dependencies..."
npm install > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""
echo "🔐 Logging in to Expo..."

# Set token as environment variable and login
export EXPO_TOKEN="$EXPO_TOKEN"
eas login --non-interactive 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Login failed. Check your token:"
    echo "   https://expo.dev/settings/account-security"
    exit 1
fi

echo "✅ Logged in to Expo"
echo ""
echo "🔨 Building APK..."
echo "⏳ This will take 5-10 minutes..."
echo ""

# Build APK
eas build --platform android --non-interactive

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║            ✅ BUILD STARTED SUCCESSFULLY!              ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📱 Your APK is being built in the cloud!"
    echo ""
    echo "Next steps:"
    echo "1. Check build status:"
    echo "   eas build:list"
    echo ""
    echo "2. Download your APK:"
    echo "   eas build:download <build-id>"
    echo ""
    echo "3. Or visit:"
    echo "   https://expo.dev/accounts/yourname/builds"
    echo ""
    echo "4. Install on phone:"
    echo "   adb install app-production.apk"
    echo ""
else
    echo "❌ Build failed"
    exit 1
fi
