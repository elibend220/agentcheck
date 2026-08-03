# 🚀 GitHub Actions - Automated APK Builder

Build your JARVIS AGI APK automatically using GitHub Actions CI/CD!

## ⚡ One-Time Setup (3 minutes)

### Step 1: Add Expo Token to Secrets

1. Go to: https://github.com/elibend220/agentcheck/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `EXPO_TOKEN`
4. **Value:** Paste your Expo token from https://expo.dev/settings/account-security
5. Click **"Add secret"**

✅ Done! GitHub now has your token securely stored.

---

## 🎯 Build Your APK

### Method 1: From GitHub Website (Easiest)

1. Go to: https://github.com/elibend220/agentcheck/actions
2. Click **"Build JARVIS AGI APK"** workflow (on left)
3. Click **"Run workflow"** (right side)
4. Choose build profile:
   - `production` - Final APK (slower, optimized)
   - `preview` - Debug APK (faster, for testing)
5. Click **"Run workflow"**
6. ⏳ Wait 5-10 minutes...
7. ✅ Download APK from **Artifacts**

### Method 2: From Terminal

```bash
# You'll need GitHub CLI installed: https://cli.github.com/

gh workflow run build-apk.yml -f build_profile=production
```

---

## 📥 Download Your APK

After build completes:

1. Go to: https://github.com/elibend220/agentcheck/actions
2. Click on the completed workflow run
3. Scroll down to **"Artifacts"**
4. Click **"jarvis-agi-apk"** to download

Or view all past builds:
- https://github.com/elibend220/agentcheck/actions/workflows/build-apk.yml

---

## 📱 Install on Phone

After downloading `app.apk`:

```bash
adb install app.apk
```

Or:
1. Copy file to phone (USB/email)
2. Open file manager
3. Tap the APK
4. Allow installation
5. Done! ✅

---

## 🔐 Security Notes

- ✅ Token stored securely in GitHub Secrets
- ✅ Never exposed in logs
- ✅ Only used for building APK
- ✅ Can regenerate token anytime

To rotate token later:
1. Go to: https://expo.dev/settings/account-security
2. Delete old token
3. Create new token
4. Update GitHub secret (Settings → Secrets → Edit EXPO_TOKEN)

---

## 🎯 Workflow Status

Check build status anytime:
- https://github.com/elibend220/agentcheck/actions

Each build shows:
- ✅ Success (APK ready)
- ⏳ In progress
- ❌ Failed (check logs)

---

## 🚀 Build Profiles

### `production`
- Full optimization
- Signed APK
- Ready for app store
- ~10 minutes

### `preview`
- Debug build
- Faster (~5 minutes)
- Good for testing
- Smaller file size

---

## 🐛 Troubleshooting

### Error: "EXPO_TOKEN not set"
**Solution:** Add token to GitHub Secrets (Step 1 above)

### Error: "Build failed"
1. Check build logs (click the failed workflow)
2. Look for error message
3. Common causes:
   - Invalid token
   - Dependencies missing
   - Network issues

### Need to rebuild?
Just click "Run workflow" again! No limit.

---

## ✨ Benefits

- ✅ No local setup needed
- ✅ Build in cloud (GitHub's servers)
- ✅ Works 24/7
- ✅ Automatic downloads
- ✅ Build history saved
- ✅ Share build link with others

---

## 📊 Example Workflow

```
You → Click "Run workflow" 
  ↓
GitHub Actions starts
  ↓
Installs dependencies
  ↓
Logs in to Expo
  ↓
Builds APK (5-10 min)
  ↓
Downloads APK
  ↓
Uploads to Artifacts
  ↓
✅ Ready to download!
```

---

## 🎉 Done!

**Your APK is now one click away!**

1. Add EXPO_TOKEN secret (one-time)
2. Click "Run workflow"
3. Download APK after build completes
4. Install on phone

That's it! 🚀

---

**Resources:**
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Expo Build Docs](https://docs.expo.dev/build/introduction/)
- [JARVIS AGI Repo](https://github.com/elibend220/agentcheck)
