# AcousticAuthApp - iOS Setup Instructions

## ✅ Files Created

All Swift files are ready in: `/Users/yernuraidarbek/Desktop/FYP/AcousticAuthApp/AcousticAuthApp/`

- ✅ AcousticAuthApp.swift (main app entry)
- ✅ ContentView.swift (UI)
- ✅ AcousticAuthenticator.swift (authentication logic)
- ✅ CryptoEngine.swift (HMAC-SHA256)
- ✅ FSKDecoder.swift (FSK audio decoding)
- ✅ Info.plist (microphone permissions)
- ✅ Assets.xcassets (app icon placeholder)

## 📱 How to Open on iPhone

### Step 1: Open in Xcode
1. Open **Xcode**
2. **File** → **Open**
3. Navigate to: `/Users/yernuraidarbek/Desktop/FYP/AcousticAuthApp/`
4. Select the **AcousticAuthApp** folder and click **Open**
5. Xcode will ask to create a project - click **Create**

### Step 2: Configure Project
1. In Xcode, click on **AcousticAuthApp** (blue icon) in the left sidebar
2. Under **Targets**, select **AcousticAuthApp**
3. Go to **Signing & Capabilities** tab
4. Check **Automatically manage signing**
5. Select your **Team** (your Apple ID)

### Step 3: Connect iPhone
1. Connect your iPhone via USB cable
2. Unlock your iPhone
3. If prompted "Trust This Computer?" → tap **Trust**
4. In Xcode, at the top, select your **iPhone** from the device dropdown (next to the Run button)

### Step 4: Run on iPhone
1. Click the **▶ Run** button (or press ⌘+R)
2. Xcode will build and install the app on your iPhone
3. First time: App will install but won't open

### Step 5: Trust Developer Certificate (First Time Only)
1. On your iPhone: **Settings** → **General** → **VPN & Device Management**
2. Find your Apple ID under "Developer App"
3. Tap it → **Trust "[Your Name]"** → **Trust**

### Step 6: Launch App
1. Go back to your iPhone home screen
2. Find and tap **AcousticAuthApp**
3. When prompted for microphone access → tap **Allow**

## 🎯 Using the App

1. **On Laptop**: Run `python src/acoustic_auth.py` (verifier mode)
2. **On iPhone**: Tap **Authenticate** button
3. The iPhone will:
   - Listen for acoustic challenge from laptop
   - Decode FSK signal
   - Compute HMAC response
   - Transmit response back to laptop
4. Check laptop terminal for authentication result

## 🔑 Important Notes

- **Shared Key**: Both laptop and iPhone use the same key (currently all zeros for testing)
- **Distance**: Keep devices within ~1 meter
- **Volume**: Set laptop speaker to medium-high volume
- **Quiet Environment**: Works best in quiet rooms

## 🛠 Troubleshooting

**"No code signing identities found"**
- Go to Xcode → Preferences → Accounts
- Add your Apple ID

**"Failed to install app"**
- Make sure iPhone is unlocked
- Try disconnecting and reconnecting USB cable

**"Microphone permission denied"**
- iPhone Settings → AcousticAuthApp → Enable Microphone

**App crashes on launch**
- Check Xcode console for error messages
- Make sure iOS version is 15.0 or higher

## 📋 Requirements

- macOS with Xcode installed
- iPhone running iOS 15.0 or later
- USB cable
- Apple ID (free)
