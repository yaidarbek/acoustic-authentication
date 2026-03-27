# Acoustic Authentication System

A secure offline peer-to-peer authentication system using acoustic (sound) communication between a laptop and iPhone. No internet, Bluetooth, or NFC required.

## How It Works

The laptop generates a cryptographic challenge, encodes it as an FSK audio signal, and plays it through its speaker. The iPhone records the signal, decodes it, computes an HMAC-SHA256 response using a shared secret, and transmits the response back acoustically. The laptop verifies the response to grant or deny access.

## Project Structure

```
acoustic-authentication/
├── src/                        # Python source code
│   ├── acoustic_auth.py        # Main authentication orchestrator
│   ├── crypto_core.py          # HMAC-SHA256 challenge-response
│   ├── working_fsk.py          # FSK modulation, Goertzel detection, Barker sync
│   ├── enhanced_fsk.py         # FSK + protocol layer integration
│   └── protocol_layer.py       # Frame structure, CRC-16 error detection
├── tests/
│   └── test_framework.py       # 33 automated test cases
├── ios/                        # iOS Swift app (in development)
├── docs/
│   └── DETAILED_DEVELOPMENT_EXPLANATION.md
├── planning/                   # Internal development notes and roadmap
├── requirements.txt
└── README.md
```

## Technical Specifications

| Component | Detail |
|---|---|
| Modulation | Frequency-Shift Keying (FSK) |
| Frequencies | 8 kHz (bit 0), 10 kHz (bit 1) |
| Sample Rate | 44.1 kHz |
| Symbol Duration | 100 ms |
| Synchronization | Barker-7 cross-correlation |
| Noise Filtering | 4th-order Butterworth bandpass (7-11 kHz) |
| Gain Control | Automatic Gain Control (AGC) |
| Frequency Detection | Goertzel algorithm |
| Cryptography | HMAC-SHA256 |
| Challenge Size | 128 bits |
| Response Size | 256 bits |
| Key Size | 256 bits |
| Error Detection | CRC-16-CCITT |
| Replay Protection | Persistent nonce log (used_nonces.json) |
| Timing Attack Prevention | hmac.compare_digest() constant-time comparison |

## Installation

```
pip install -r requirements.txt
```

## Running

```
cd src
python acoustic_auth.py
```

## Running Tests

```
cd tests
python test_framework.py
```

**Current test results: 33/33 passing (100%)**

| Test Class | Tests |
|---|---|
| TestCryptographicCore | 4 |
| TestAuthenticationProtocol | 3 |
| TestFSKAudio | 8 |
| TestProtocolLayer | 10 |
| TestSystemIntegration | 3 |
| TestSecurityFeatures | 2 |
| PerformanceBenchmarks | 3 |

## Security Properties

- Replay attack prevention — used challenges persisted to disk across sessions
- Timing attack resistance — constant-time HMAC comparison
- Session timeout — 30 second expiry
- 128-bit challenge entropy — 2^128 possible values
- Proximity enforcement — acoustic channel limits range to ~1 metre

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
| 33 automated tests | Done |
| iOS Swift app | In progress |
| GUI | Planned |
| Hardware frequency test | Pending |

## Dependencies

- Python 3.8+
- pyaudio 0.2.11
- numpy 1.24.3
- scipy 1.10.1

## Academic Context

Final Year Project — BSc Computer Science, City University of Hong Kong, 2025-2026.
Supervisor: Prof. Gerhard Hancke.
