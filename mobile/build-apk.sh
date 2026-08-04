#!/bin/bash

# 🚀 JARVIS AGI - APK Builder Script
# בנייה קלה של APK ל-Android

echo "╔════════════════════════════════════════════════════════╗"
echo "║          JARVIS AGI - APK Builder Helper               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# בדוק אם Node.js מותקן
if ! command -v node &> /dev/null; then
    echo "❌ Node.js לא מותקן. בקר ב https://nodejs.org/"
    exit 1
fi

# בדוק אם Java מותקן
if ! command -v java &> /dev/null; then
    echo "❌ Java לא מותקן. בקר ב https://www.oracle.com/java/technologies/downloads/"
    exit 1
fi

# בדוק אם ANDROID_HOME מוגדר
if [ -z "$ANDROID_HOME" ]; then
    echo "⚠️  ANDROID_HOME לא מוגדר"
    echo ""
    echo "הגדר את ANDROID_HOME:"
    echo "  macOS:  export ANDROID_HOME=\$HOME/Library/Android/Sdk"
    echo "  Linux:  export ANDROID_HOME=\$HOME/Android/Sdk"
    echo "  Windows: set ANDROID_HOME=C:\\Users\\YourName\\AppData\\Local\\Android\\Sdk"
    echo ""
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ Java: $(java -version 2>&1 | head -n 1)"
echo "✅ ANDROID_HOME: $ANDROID_HOME"
echo ""

# בחר סוג בנייה
echo "איזה סוג בנייה?"
echo "1) Debug (מהיר, עבור בדיקות)"
echo "2) Release (איטי יותר, עבור הפצה)"
echo ""
read -p "בחר (1 או 2): " BUILD_TYPE

if [ "$BUILD_TYPE" = "1" ]; then
    BUILD_VARIANT="Debug"
    BUILD_CMD="assembleDebug"
    APK_PATH="android/app/build/outputs/apk/debug/app-debug.apk"
    echo "🔧 בנייה Debug..."
elif [ "$BUILD_TYPE" = "2" ]; then
    BUILD_VARIANT="Release"
    BUILD_CMD="assembleRelease"
    APK_PATH="android/app/build/outputs/apk/release/app-release.apk"
    echo "🔧 בנייה Release..."
else
    echo "❌ בחר 1 או 2"
    exit 1
fi

# התקן dependencies אם צריך
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 התקנת dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ npm install נכשל"
        exit 1
    fi
fi

# בנייה
echo ""
echo "🔨 בנייה של $BUILD_VARIANT APK..."
echo ""

cd android

if [ ! -f "gradlew" ]; then
    echo "❌ gradlew לא נמצא"
    exit 1
fi

chmod +x gradlew
./gradlew $BUILD_CMD

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ הבנייה נכשלה!"
    echo ""
    echo "נסה את זה:"
    echo "  cd android"
    echo "  ./gradlew clean"
    echo "  ./gradlew $BUILD_CMD"
    exit 1
fi

cd ..

# בדוק אם ה-APK נוצר
if [ ! -f "$APK_PATH" ]; then
    echo "❌ APK לא נמצא ב: $APK_PATH"
    exit 1
fi

APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║            ✅ בנייה הסתיימה בהצלחה!                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📱 APK Location: $APK_PATH"
echo "📊 File Size: $APK_SIZE"
echo ""
echo "השלבים הבאים:"
echo ""
echo "1️⃣  התקנה על טלפון המחובר:"
echo "   adb install \"$APK_PATH\""
echo ""
echo "2️⃣  התקנה עם adb push (אם adb לא זמין):"
echo "   העתק את הקובץ לטלפון ותקן ידנית"
echo ""
echo "3️⃣  הגדרות בטלפון:"
echo "   - פתח את JARVIS AGI"
echo "   - לחץ Settings"
echo "   - הזן את URL של Backend (http://192.168.1.X:8000 או https://server.com)"
echo ""
echo "4️⃣  ודא שה-Backend פועל:"
echo "   cd backend"
echo "   python server.py"
echo ""
echo "🎉 הכל מוכן!"
