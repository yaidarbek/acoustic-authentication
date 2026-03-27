# iOS App — AcousticAuth

SwiftUI iPhone app implementing the **prover** side of the acoustic authentication protocol.

## Role in the System

The iPhone acts as the prover:
1. Listens for FSK-encoded challenge from the laptop speaker
2. Decodes the challenge using the Goertzel algorithm
3. Computes HMAC-SHA256 response using the shared secret
4. Transmits the response back to the laptop via FSK audio

## File Structure

```
AcousticAuth/
├── AcousticAuthApp.swift       # App entry point (@main)
├── ContentView.swift           # SwiftUI interface
├── AcousticAuthenticator.swift # Protocol orchestration + AVAudioEngine
├── FSKDecoder.swift            # Goertzel detection, Barker sync, AGC
└── CryptoEngine.swift          # HMAC-SHA256 via Apple CryptoKit
```

## How to Open in Xcode

1. Open Xcode
2. File → Open → select `ios/AcousticAuth/` folder
3. Xcode will detect the Swift files — create a new project and add them, or use an existing project

## Creating the Xcode Project

1. Xcode → Create New Project → iOS → App
2. Product Name: `AcousticAuth`
3. Interface: SwiftUI
4. Language: Swift
5. Delete the default `ContentView.swift` Xcode creates
6. Drag all 5 Swift files from this folder into the project navigator
7. Add `AVFoundation` and `CryptoKit` frameworks (they are system frameworks, no install needed)

## Required Permissions (Info.plist)

Add these keys to `Info.plist`:
```xml
<key>NSMicrophoneUsageDescription</key>
<string>Required to receive acoustic authentication challenges</string>
```

## Shared Key Setup

The shared key in `ContentView.swift` must match the key on the laptop side.

For testing, hardcode the same hex key in both:
- iOS: `sharedKeyHex` in `ContentView.swift`
- Python: pass `bytes.fromhex("your_key_here")` to `AcousticAuthenticator()`

In production, the key would be exchanged once during device pairing and stored in the iOS Keychain using `SecItemAdd`.

## Mirrors Python Implementation

| Swift File | Python Equivalent |
|---|---|
| `CryptoEngine.swift` | `src/crypto_core.py` CryptographicCore |
| `FSKDecoder.swift` | `src/working_fsk.py` WorkingFSK |
| `AcousticAuthenticator.swift` | `src/acoustic_auth.py` AcousticAuthenticator (prover role) |
| `ContentView.swift` | `src/gui.py` AuthGUI |

## Status

- [x] CryptoEngine — HMAC-SHA256 via CryptoKit
- [x] FSKDecoder — Goertzel, AGC, Barker sync
- [x] AcousticAuthenticator — full protocol flow with AVAudioEngine
- [x] ContentView — SwiftUI interface
- [ ] Hardware integration testing (pending Xcode + iPhone)
- [ ] Keychain integration for shared key storage
- [ ] Real-world noise testing
