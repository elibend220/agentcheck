@echo off
REM 🚀 JARVIS AGI - APK Builder Script for Windows

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║          JARVIS AGI - APK Builder Helper (Windows)     ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM בדוק אם Node.js מותקן
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js לא מותקן. בקר ב https://nodejs.org/
    exit /b 1
)

REM בדוק אם Java מותקן
java -version >nul 2>&1
if errorlevel 1 (
    echo ❌ Java לא מותקן. בקר ב https://www.oracle.com/java/technologies/downloads/
    exit /b 1
)

REM בדוק אם ANDROID_HOME מוגדר
if "%ANDROID_HOME%"=="" (
    echo ⚠️  ANDROID_HOME לא מוגדר
    echo.
    echo הגדר את ANDROID_HOME:
    echo   set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk
    echo.
    echo לאחר מכן, הפעל את הסקריפט שוב.
    exit /b 1
)

echo ✅ Node.js installed
for /f "tokens=*" %%i in ('node --version') do echo    Version: %%i
echo ✅ Java installed
echo ✅ ANDROID_HOME: %ANDROID_HOME%
echo.

REM בחר סוג בנייה
echo איזה סוג בנייה?
echo 1) Debug (מהיר, עבור בדיקות)
echo 2) Release (איטי יותר, עבור הפצה)
echo.
set /p BUILD_TYPE="בחר (1 או 2): "

if "%BUILD_TYPE%"=="1" (
    set BUILD_VARIANT=Debug
    set BUILD_CMD=assembleDebug
    set APK_PATH=android\app\build\outputs\apk\debug\app-debug.apk
    echo 🔧 בנייה Debug...
) else if "%BUILD_TYPE%"=="2" (
    set BUILD_VARIANT=Release
    set BUILD_CMD=assembleRelease
    set APK_PATH=android\app\build\outputs\apk\release\app-release.apk
    echo 🔧 בנייה Release...
) else (
    echo ❌ בחר 1 או 2
    exit /b 1
)

REM התקן dependencies אם צריך
if not exist "node_modules" (
    echo.
    echo 📦 התקנת dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ npm install נכשל
        exit /b 1
    )
)

REM בנייה
echo.
echo 🔨 בנייה של %BUILD_VARIANT% APK...
echo.

cd android

if not exist "gradlew.bat" (
    echo ❌ gradlew.bat לא נמצא
    exit /b 1
)

call gradlew.bat %BUILD_CMD%

if errorlevel 1 (
    echo.
    echo ❌ הבנייה נכשלה!
    echo.
    echo נסה את זה:
    echo   cd android
    echo   gradlew.bat clean
    echo   gradlew.bat %BUILD_CMD%
    cd ..
    exit /b 1
)

cd ..

REM בדוק אם ה-APK נוצר
if not exist "%APK_PATH%" (
    echo ❌ APK לא נמצא ב: %APK_PATH%
    exit /b 1
)

REM קבל גודל הקובץ
for %%F in ("%APK_PATH%") do set APK_SIZE=%%~zF

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║            ✅ בנייה הסתיימה בהצלחה!                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📱 APK Location: %APK_PATH%
echo 📊 File Size: %APK_SIZE% bytes
echo.
echo השלבים הבאים:
echo.
echo 1️⃣  התקנה על טלפון המחובר:
echo    adb install "%APK_PATH%"
echo.
echo 2️⃣  אם adb לא זמין:
echo    - העתק את הקובץ לטלפון
echo    - תקן ידנית (לחץ על הקובץ בקובץ מנהל)
echo.
echo 3️⃣  הגדרות בטלפון:
echo    - פתח את JARVIS AGI
echo    - לחץ Settings
echo    - הזן את URL של Backend
echo      (http://192.168.1.X:8000 או https://server.com)
echo.
echo 4️⃣  ודא שה-Backend פועל:
echo    cd backend
echo    python server.py
echo.
echo 🎉 הכל מוכן!
echo.
pause
