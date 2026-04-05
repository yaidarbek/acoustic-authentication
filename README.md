# Acoustic Authentication System

A secure offline peer-to-peer authentication system using acoustic (sound) communication between a laptop and iPhone. No internet, Bluetooth, or NFC required.

## How It Works

The laptop generates a cryptographic challenge, encodes it as an FSK audio signal, and plays it through its speaker. The iPhone records the signal, decodes it, computes an HMAC-SHA256 response using a shared secret, and transmits the response back acoustically. The laptop verifies the response to grant or deny access.

## Project Structure

```
acoustic-authentication/
├── src/                        # Python source code (laptop / verifier)
│   ├── acoustic_auth.py        # Main authentication orchestrator (4-phase protocol)
│   ├── crypto_core.py          # HMAC-SHA256 challenge-response, nonce management
│   ├── working_fsk.py          # FSK modulation, Goertzel detection, Barker-7 sync
│   ├── enhanced_fsk.py         # FSK + protocol layer integration
│   ├── protocol_layer.py       # Frame structure, CRC-16-CCITT error detection
│   ├── tone_utils.py           # Handshake tone generation and detection
│   ├── secure_storage.py       # Fernet-encrypted file vault (post-auth access)
│   ├── gui.py                  # Desktop GUI (tkinter)
│   ├── laptop_sim.py           # File-based laptop simulator (no audio hardware)
│   ├── iphone_sim.py           # File-based iPhone simulator (no audio hardware)
│   └── sim_channel.py          # Shared file-based IPC channel for simulation
├── Ios_FYP/                    # iOS Swift app (iPhone / prover)
│   └── Ios_FYP/
│       ├── AcousticAuthenticator.swift  # State machine, full auth cycle
│       ├── FSKDecoder.swift             # Goertzel, AGC, Barker sync, FSK decode/encode
│       ├── CryptoEngine.swift           # HMAC-SHA256 via Apple CryptoKit
│       └── ContentView.swift            # SwiftUI interface
├── tests/
│   └── test_framework.py       # 33 automated test cases
├── docs/
│   └── DETAILED_DEVELOPMENT_EXPLANATION.md
├── planning/                   # Development notes and roadmap
├── requirements.txt
└── README.md
```

## Technical Specifications

| Component | Detail |
|---|---|
| Modulation | Frequency-Shift Keying (FSK) |
| Frequencies | 7 kHz (bit 0), 9 kHz (bit 1) |
| Sample Rate | 44.1 kHz |
| Symbol Duration | 150 ms |
| Synchronization | Barker-7 cross-correlation (3-stage hierarchical search) |
| Noise Filtering | 4th-order Butterworth bandpass (6–10 kHz) |
| Gain Control | Automatic Gain Control (AGC) |
| Frequency Detection | Goertzel algorithm |
| Cryptography | HMAC-SHA256 |
| Challenge Size | 32 bits |
| Response Size | 64 bits (truncated HMAC) |
| Key Size | 256 bits |
| Error Detection | CRC-16-CCITT |
| Replay Protection | Persistent nonce log (used_nonces.json) |
| Timing Attack Prevention | hmac.compare_digest() constant-time comparison |
| Session Timeout | 120 seconds |
| Effective Range | ~1 metre |

## Protocol Phases

| Phase | Description |
|---|---|
| Phase 1 — Beacon | Laptop broadcasts READY tone (11 kHz). iPhone responds with ACK (13 kHz). |
| Phase 2 — Sync | Laptop sends Barker-7 preamble + 16-bit FSK sync pattern. iPhone ACKs. |
| Phase 3 — Challenge | Laptop sends 32-bit FSK-encoded cryptographic challenge. iPhone ACKs. |
| Phase 4 — Response | iPhone transmits 64-bit truncated HMAC-SHA256 response. Laptop verifies and sends result tone. |

## Installation

```
pip install -r requirements.txt
```

## Running

### GUI (recommended)
```
cd src
python gui.py
```

### Headless
```
cd src
python acoustic_auth.py
```

### Simulation (no audio hardware required)
Run in two separate terminals:
```
# Terminal 1
cd src
python laptop_sim.py

# Terminal 2
cd src
python iphone_sim.py
```

## Running the iOS App (iPhone / Prover)

### Requirements
- macOS with Xcode 14+
- iPhone with iOS 15.0 or later
- Apple Developer account (free tier is sufficient)

### Steps

**1. Open the project in Xcode**
```
open Ios_FYP/Ios_FYP.xcodeproj
```

**2. Configure signing**
1. Click `Ios_FYP` (blue icon) in the Xcode left sidebar
2. Select `Ios_FYP` under TARGETS
3. Go to the `Signing & Capabilities` tab
4. Enable `Automatically manage signing`
5. Select your Apple ID under Team

**3. Build and run on iPhone**
1. Connect iPhone via USB and unlock it
2. Select your iPhone from the device dropdown in the Xcode toolbar
3. Press `⌘+R` or click the Run button
4. If prompted on iPhone: `Settings → General → VPN & Device Management → Trust`
5. Allow microphone access when the app first launches

### Usage
1. Start the laptop verifier first: `python src/gui.py`
2. Tap `Authenticate` on the iPhone app
3. Place devices within ~1 metre of each other
4. The app handles the full 4-phase protocol automatically

> For more detail see `Ios_FYP/README.md`

---

## Running Tests

```
cd tests
python test_framework.py
```

**Current test results: 33/33 passing (100%)**

| Test Class | Tests | What is tested |
|---|---|---|
| TestCryptographicCore | 4 | Challenge generation, HMAC-SHA256, verification, replay prevention |
| TestAuthenticationProtocol | 3 | Full auth cycle, wrong-key rejection, session timeout |
| TestFSKAudio | 8 | Tone generation, Goertzel detection, bandpass filter, AGC, Barker sync |
| TestProtocolLayer | 10 | Frame roundtrip, CRC corruption detection, large data splitting |
| TestSystemIntegration | 3 | Bytes↔bits conversion, challenge/response bit sizes |
| TestSecurityFeatures | 2 | Timing attack resistance, key entropy |
| PerformanceBenchmarks | 3 | Challenge generation, HMAC throughput, full auth cycle timing |

## Security Properties

- Replay attack prevention — used challenges persisted to disk across sessions
- Timing attack resistance — constant-time HMAC comparison via hmac.compare_digest()
- Session timeout — 120 second expiry
- 32-bit challenge nonce — persistent uniqueness enforced across restarts
- Proximity enforcement — acoustic channel limits effective range to ~1 metre
- Post-auth file encryption — Fernet (AES-128-CBC + HMAC-SHA256) via secure_storage.py

## Status

| Component | Status |
|---|---|
| FSK audio pipeline | Done |
| Bandpass filter | Done |
| AGC normalization | Done |
| Barker-7 sync | Done |
| HMAC-SHA256 crypto | Done |
| CRC-16 protocol layer | Done |
| Persistent nonce logging | Done |
| Secure file storage | Done |
| Desktop GUI | Done |
| iOS Swift app | Done |
| File-based simulation | Done |
| 33 automated tests | Done |

## Dependencies

- Python 3.8+
- pyaudio 0.2.11
- numpy 1.24.3
- scipy 1.10.1
- cryptography ≥43.0.0

## Academic Context

Final Year Project — BSc Computer Science, City University of Hong Kong, 2025-2026.
Supervisor: Prof. Gerhard Hancke.
