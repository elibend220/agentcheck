# 🚀 Build APK Now - Automated Guide

עכשיו שיש לך חשבון Expo, אתה יכול לבנות את ה-APK בקליק אחד!

## 🎯 שלוש דקות עד ל-APK

### שלב 1: קבל את ה-Token שלך

1. בקר ב: https://expo.dev/settings/account-security
2. לחץ **"Create Token"** (או copy token קיים)
3. שם: `jarvis-build`
4. **העתק את הטוקן** (משהו כמו: `expo_abc123...`)
5. **הדבק לצד** (תצטרך בעוד שניה)

### שלב 2: בחר את השיטה שלך

#### **Option A: Codespace (אם פתוחה)**
```bash
cd mobile
./build-apk-automated.sh <PASTE_YOUR_TOKEN_HERE>
```

#### **Option B: Mac/Linux (מקומי)**
```bash
cd mobile
chmod +x build-apk-automated.sh
./build-apk-automated.sh <PASTE_YOUR_TOKEN_HERE>
```

#### **Option C: Windows (מקומי)**
```bash
cd mobile
build-apk-automated.bat <PASTE_YOUR_TOKEN_HERE>
```

### שלב 3: החלף את ה-Token

**בכל אחת מהשיטות לעיל, החלף:**
```
<PASTE_YOUR_TOKEN_HERE>
```

**עם ה-Token שלך מ-Step 1**

**דוגמה:**
```bash
./build-apk-automated.sh expo_abc123xyz789...
```

### שלב 4: המתן!

```
✅ Expo token received
📦 Installing dependencies...
✅ Dependencies installed
🔐 Logging in to Expo...
✅ Logged in to Expo
🔨 Building APK...
⏳ This will take 5-10 minutes...
```

**הבנייה מתחילה בענן של Expo!** ☁️

## 📱 לאחר הבנייה

### Check Build Status
```bash
eas build:list
```

### Download APK
```bash
eas build:download <BUILD_ID>
```

### Or Visit Website
```
https://expo.dev/accounts/yourname/builds
```

### Install on Phone
```bash
adb install app-production.apk
```

## ✅ סיכום

| שלב | מה לעשות | קלט |
|-----|---------|------|
| 1 | קבל token | https://expo.dev/settings/account-security |
| 2 | בחר script | build-apk-automated.sh (Mac/Linux) או .bat (Windows) |
| 3 | הרץ עם token | `./build-apk-automated.sh TOKEN` |
| 4 | המתן | 5-10 דקות |
| 5 | הורד APK | eas build:list + eas build:download |
| 6 | התקן | adb install app.apk |

## 🎉 זהו!

שקע, תרים קפה, וחכה! ה-APK בנייה מתחילה... ☁️

---

**בעיות?** ראה [EAS_BUILD_GUIDE.md](../EAS_BUILD_GUIDE.md)
