# 📱 הנחיות בנייה של APK ל-JARVIS AGI

## ✅ דרישות מקדימות

לפני שתתחיל, ודא שיש לך:

### 1️⃣ Android Studio
- הורד מ: https://developer.android.com/studio
- התקן את כל הרכיבים הנדרשים (SDK, NDK, Emulator)

### 2️⃣ Java Development Kit (JDK)
```bash
# בדוק אם Java מותקן
java -version

# אם לא, התקן JDK 11 או גבוה יותר
# macOS:
brew install openjdk@11

# Linux:
sudo apt-get install openjdk-11-jdk

# Windows:
# הורד מ https://www.oracle.com/java/technologies/downloads/
```

### 3️⃣ Node.js ו-npm
```bash
# בדוק גרסות
node --version
npm --version

# אם לא מותקן, הורד מ https://nodejs.org/
```

### 4️⃣ React Native CLI (אופציונלי)
```bash
npm install -g react-native-cli
```

## 🚀 שלבי הבנייה

### שלב 1: הגדרת משתנים סביבתיים (ANDROID_HOME)

**macOS/Linux:**
```bash
# הוסף לקובץ ~/.bashrc או ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/Sdk  # macOS
export ANDROID_HOME=$HOME/Android/Sdk          # Linux
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/emulator

# העלה את השינויים לתוקף
source ~/.bashrc  # או source ~/.zshrc
```

**Windows (PowerShell כמנהל):**
```powershell
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Users\YourUsername\AppData\Local\Android\Sdk", "User")
```

### שלב 2: הכנת הפרויקט

```bash
# נווט לתיקיית mobile
cd /path/to/agentcheck/mobile

# התקן dependencies
npm install

# אם צריך, נקה cache
npm cache clean --force
```

### שלב 3: בנייה ראשונה (Debug APK - מהיר יותר)

```bash
# אפשרות 1: בעזרת npm script
npm run android

# אפשרות 2: בעזרת Gradle ישירות
cd android
./gradlew assembleDebug
cd ..

# ה-APK יהיה ב:
# android/app/build/outputs/apk/debug/app-debug.apk
```

### שלב 4: בנייה ל-Release (APK סופי - אם רוצה להפץ)

```bash
cd android

# בנייה יחידה (ללא חתימה)
./gradlew assembleRelease

# או לתוצאה כוללת (עם חתימה אוטומטית)
./gradlew bundleRelease

cd ..

# ה-APK יהיה ב:
# android/app/build/outputs/apk/release/app-release.apk
```

## 📦 התקנת APK על הטלפון

### דרך 1: פעילות ישירה (אם מחובר ל-Android Studio)

```bash
cd android
./gradlew installDebug
cd ..
```

### דרך 2: העתקה ידנית של הקובץ

```bash
# בחר את הנתיב המתאים:
# לדוגמה:
adb install android/app/build/outputs/apk/debug/app-debug.apk

# או העתק את הקובץ להתקנה ידנית על הטלפון
```

### דרך 3: בעזרת Android Studio

1. פתח Android Studio
2. לחץ על `Build` → `Build Bundle(s) / APK(s)` → `Build APK(s)`
3. Android Studio תבנה בעבורך
4. לחץ על `Locate` כדי למצוא את ה-APK
5. העתק את הקובץ לטלפון

## ⚙️ הגדרות חשובות

### API URL בטלפון

כשתפתח את האפליקציה בפעם הראשונה:

1. לחץ על **Settings** (הגדרות)
2. הזן את ה-URL של ה-Backend:
   - **Local Development:** `http://192.168.1.X:8000` (החלף X בכתובת ה-IP של המחשב)
   - **Remote Server:** `https://your-server.com`

### הפעלת Backend

```bash
cd /path/to/agentcheck/backend

# התקן dependencies
pip install -r requirements.txt

# הפעל את ה-Server
python server.py

# Server יפעל ב-http://localhost:8000
```

## 🐛 פתרון בעיות נפוצות

### Error: "ANDROID_HOME is not set"
```bash
# ודא שהגדרת את ANDROID_HOME נכון
echo $ANDROID_HOME

# אם קיבלת ריק, הגדר אותו:
export ANDROID_HOME=$HOME/Library/Android/Sdk  # macOS
export ANDROID_HOME=$HOME/Android/Sdk          # Linux
```

### Error: "Gradle build failed"
```bash
# נקה את ה-cache של Gradle
cd android
./gradlew clean
./gradlew assembleDebug
cd ..
```

### Error: "Cannot find module" (Node modules חסרים)
```bash
cd mobile
rm -rf node_modules package-lock.json
npm install
```

### טלפון לא מחובר
```bash
# בדוק חיבור ADB
adb devices

# אם לא מופיע, תקן:
# 1. פעל הרשאות USB בטלפון (Settings → Developer Options)
# 2. חבר מחדש את הטלפון
# 3. בחר "Transfer Files" במצב USB
```

## 📊 מידע על הבנייה

**Project Details:**
- Application ID: `com.jarvis.mobile`
- Version: 1.0.0
- Min SDK: 24 (Android 7.0)
- Target SDK: 33 (Android 13)
- Java: 11+

**Features:**
- ✅ Chat Interface (GiftedChat)
- ✅ Session Management
- ✅ Real-time Metrics
- ✅ Offline Support
- ✅ User Sandboxing
- ✅ Autonomous Search

## 🎯 שלבים מסכמים (טיול מהיר)

```bash
# 1. נווט לתיקיית הפרויקט
cd mobile

# 2. התקן dependencies
npm install

# 3. בנה את ה-APK (Debug)
cd android
./gradlew assembleDebug
cd ..

# 4. ה-APK מוכן ב: android/app/build/outputs/apk/debug/app-debug.apk

# 5. התקן על טלפון
adb install android/app/build/outputs/apk/debug/app-debug.apk

# 6. בטלפון, הגדר את API URL בהגדרות
# ודא שה-Backend פועל ב-http://localhost:8000 (או IP הנכון)
```

## ❓ עזרה נוספת

אם נתקלת בבעיות:

1. בדוק את ה-logs: `adb logcat`
2. וודא שה-Backend פועל ונגיש
3. בדוק חיבור אינטרנט (אם Backend מרוחק)
4. ודא שהטלפון ב-Developer Mode (Settings → About Phone → לחץ 7 פעמים על Build Number)

---

**Good luck! 🚀**
