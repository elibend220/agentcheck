# 🚀 EAS Build Quick Start

צעדים מהירים לבנייה של APK ב-5 דקות.

## שלב 1: חשבון Expo (חד פעמי)

1. בקר ב https://expo.dev/signup
2. צור חשבון עם אימייל (או Google/GitHub)
3. אשר את האימייל שלך
4. בקר ב https://expo.dev/settings/account-security
5. לחץ "Create Token"
6. בחר שם: `jarvis-build`
7. **העתק את הטוקן** (תצטרך אותו בעוד שניה)

## שלב 2: התחברות ל-EAS CLI

```bash
cd mobile
eas login
# הדבק את הטוקן שקיבלת בשלב 1
# לחץ Enter
```

## שלב 3: בנייה

```bash
eas build --platform android
```

כשתשאלו אותך:
- **Which platform would you like to build for?** → `android` (אל תשנה)
- **Which eas build profile do you want to use?** → `production` (אפשר גם `preview`)
- **Name your build** → `jarvis-v1.0` (כל שם שתרצה)

**סוף זה!** EAS יבנה את ה-APK בענן.

## שלב 4: המתן להבנייה

```
✨ Build queued...
📱 Build in progress...
⏳ This usually takes 5-10 minutes
```

דפדף לקישור הבנייה כדי לראות התקדמות:
```
https://expo.dev/accounts/yourname/builds/...
```

## שלב 5: הורד את ה-APK

כאשר הבנייה תסתיים:
1. לחץ על **Download APK** בדף הבנייה
2. או הרץ: `eas build:list` כדי לראות בנייות קודמות
3. להורדה: `eas build:download <build-id>`

## שלב 6: התקנה על הטלפון

```bash
# בחר אחד מהשניים:

# אפשרות 1: ADB (אם מחובר)
adb install app-production-xxx.apk

# אפשרות 2: העתק ידנית
# 1. העתק את ה-APK לטלפון (דרך USB)
# 2. פתח קובץ מנהל
# 3. לחץ על הקובץ
# 4. אשר התקנה
```

## שלב 7: הגדרות

1. פתח את **JARVIS AGI** בטלפון
2. לחץ על **Settings** (בתחתית)
3. הזן את **API URL**:
   ```
   http://192.168.1.X:8000
   ```
   (החלף X בכתובת ה-IP של המחשב שלך)

4. ודא שה-Backend פועל:
   ```bash
   cd backend
   python server.py
   ```

## ✅ סיום!

האפליקציה מוכנה! 🎉

---

**בעיות?** ראה [EAS_BUILD_GUIDE.md](../EAS_BUILD_GUIDE.md) לפתרונות מפורטים.
