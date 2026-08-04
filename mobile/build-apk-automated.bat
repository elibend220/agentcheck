@echo off
REM 🚀 JARVIS AGI - Automated APK Builder
REM Usage: build-apk-automated.bat YOUR_EXPO_TOKEN

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║          JARVIS AGI - Automated APK Builder             ║
echo ║              (Powered by EAS Build)                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if token provided
if "%1"=="" (
    echo ❌ Error: Expo token required
    echo.
    echo Usage: build-apk-automated.bat YOUR_EXPO_TOKEN
    echo.
    echo To get your token:
    echo 1. Go to: https://expo.dev/settings/account-security
    echo 2. Create token (or copy existing one)
    echo 3. Run: build-apk-automated.bat ^<paste-token-here^>
    echo.
    pause
    exit /b 1
)

set EXPO_TOKEN=%1

REM Verify we're in mobile directory
if not exist "package.json" (
    echo ❌ Error: package.json not found
    echo Make sure you're in the mobile directory
    pause
    exit /b 1
)

echo ✅ Expo token received
echo 📦 Installing dependencies...
call npm install >nul 2>&1

if errorlevel 1 (
    echo ❌ npm install failed
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.
echo 🔐 Logging in to Expo...

REM Set token and login
set EXPO_TOKEN=%EXPO_TOKEN%
call eas login --non-interactive >nul 2>&1

if errorlevel 1 (
    echo ❌ Login failed. Check your token:
    echo    https://expo.dev/settings/account-security
    pause
    exit /b 1
)

echo ✅ Logged in to Expo
echo.
echo 🔨 Building APK...
echo ⏳ This will take 5-10 minutes...
echo.

REM Build APK
call eas build --platform android --non-interactive

if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║            ✅ BUILD STARTED SUCCESSFULLY!              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📱 Your APK is being built in the cloud!
echo.
echo Next steps:
echo 1. Check build status:
echo    eas build:list
echo.
echo 2. Download your APK:
echo    eas build:download ^<build-id^>
echo.
echo 3. Or visit:
echo    https://expo.dev/accounts/yourname/builds
echo.
echo 4. Install on phone:
echo    adb install app-production.apk
echo.
pause
