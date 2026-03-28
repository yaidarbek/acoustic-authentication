# Ios_FYP - Acoustic Authentication iOS App

## ✅ Setup Complete!

All Swift files have been added to your Xcode project:
- ✅ Ios_FYPApp.swift (main app)
- ✅ ContentView.swift (UI)
- ✅ AcousticAuthenticator.swift (authentication logic)
- ✅ CryptoEngine.swift (HMAC-SHA256)
- ✅ FSKDecoder.swift (FSK audio decoding)
- ✅ Info.plist (microphone permissions)

## 📱 How to Run on iPhone

### Step 1: Open in Xcode
The project is already open, or you can open it:
```bash
open /Users/yernuraidarbek/Desktop/FYP/Ios_FYP/Ios_FYP.xcodeproj
```

### Step 2: Configure Signing
1. In Xcode, click **Ios_FYP** (blue icon) in left sidebar
2. Select **Ios_FYP** under TARGETS
3. Go to **Signing & Capabilities** tab
4. Check **Automatically manage signing**
5. Select your **Team** (Apple ID)

### Step 3: Connect iPhone & Run
1. Connect iPhone via USB
2. Unlock iPhone and trust computer if prompted
3. In Xcode toolbar, select your **iPhone** from device dropdown
4. Click **▶ Run** button (or press ⌘+R)

### Step 4: Trust Developer (First Time Only)
1. On iPhone: **Settings** → **General** → **VPN & Device Management**
2. Tap your Apple ID → **Trust**
3. Launch the app from home screen
4. Allow microphone access when prompted

## 🎯 Using the App

1. **On Laptop**: 
   ```bash
   cd /Users/yernuraidarbek/Desktop/FYP/src
   python acoustic_auth.py
   ```
   Choose verifier mode

2. **On iPhone**: 
   - Tap **Authenticate** button
   - App will listen for acoustic challenge
   - Decode FSK signal
   - Compute HMAC response
   - Transmit response back

3. **Check laptop terminal** for authentication result

## 🔑 Configuration

- **Shared Key**: Currently set to all zeros (for testing)
- **Frequencies**: 8 kHz (bit 0), 10 kHz (bit 1)
- **Sample Rate**: 44.1 kHz
- **Symbol Duration**: 100 ms

## 📋 Requirements

- iOS 15.0 or later
- Microphone access
- Quiet environment for best results
- Laptop and iPhone within ~1 meter

## 🛠 Troubleshooting

**Build errors in Xcode?**
- Make sure all 5 Swift files are in the project navigator
- Check that Info.plist has microphone permission

**App crashes?**
- Check Xcode console for errors
- Verify iOS version is 15.0+

**No sound detected?**
- Increase laptop volume
- Reduce background noise
- Move devices closer together

**"Microphone permission denied"?**
- iPhone Settings → Ios_FYP → Enable Microphone
