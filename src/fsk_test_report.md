# FSK Signal Processing Test Report
Generated: 2026-03-29 19:21:57

## Configuration
| Parameter | Value |
|-----------|-------|
| Sample rate | 44100 Hz |
| f0 (bit 0) | 7000 Hz |
| f1 (bit 1) | 9000 Hz |
| Symbol duration | 150 ms |
| Guard interval | 200 ms |
| Samples per symbol | 6615 |

## 1. Sync Pattern Tests

### Test: sync_clean
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: clean (no noise)
- Signal length: 183015 samples (4.150s)
- Encode time: 7.5ms
- Signal saved to: `sync_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 176.3ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 104.71 | 3021.79 | `1` |
| 1 | 3038.76 | 104.15 | `0` |
| 2 | 104.71 | 3021.79 | `1` |
| 3 | 3038.76 | 104.15 | `0` |
| 4 | 104.71 | 3021.79 | `1` |
| 5 | 3038.76 | 104.15 | `0` |
| 6 | 104.71 | 3021.79 | `1` |
| 7 | 3038.76 | 104.15 | `0` |

### Test: sync_30dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 30 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 5.4ms
- Signal saved to: `sync_30dB.npy`
- Max amplitude: 0.1067
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 168.9ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 101.24 | 2943.54 | `1` |
| 1 | 2960.79 | 101.28 | `0` |
| 2 | 102.13 | 2943.91 | `1` |
| 3 | 2960.09 | 103.11 | `0` |
| 4 | 102.87 | 2941.72 | `1` |
| 5 | 2960.75 | 100.25 | `0` |
| 6 | 103.45 | 2945.55 | `1` |
| 7 | 2960.20 | 101.75 | `0` |

### Test: sync_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 20 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 5.9ms
- Signal saved to: `sync_20dB.npy`
- Max amplitude: 0.1233
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 128.9ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 98.79 | 2783.25 | `1` |
| 1 | 2805.28 | 100.53 | `0` |
| 2 | 98.36 | 2783.03 | `1` |
| 3 | 2795.46 | 95.55 | `0` |
| 4 | 92.80 | 2785.76 | `1` |
| 5 | 2795.21 | 99.33 | `0` |
| 6 | 100.30 | 2782.72 | `1` |
| 7 | 2796.41 | 98.89 | `0` |

### Test: sync_10dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 10 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 4.5ms
- Signal saved to: `sync_10dB.npy`
- Max amplitude: 0.1814
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 141.2ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 80.12 | 2325.31 | `1` |
| 1 | 2322.69 | 82.53 | `0` |
| 2 | 71.46 | 2325.20 | `1` |
| 3 | 2342.45 | 77.53 | `0` |
| 4 | 68.75 | 2305.98 | `1` |
| 5 | 2328.68 | 80.15 | `0` |
| 6 | 82.41 | 2307.13 | `1` |
| 7 | 2340.97 | 76.70 | `0` |

## 2. Challenge Tests (32 bits)
Challenge bytes: `586923b7`

### Test: challenge_clean
- Input bits: `01011000011010010010001110110111`
- Bit count: 32
- SNR: clean (no noise)
- Signal length: 288855 samples (6.550s)
- Encode time: 20.5ms
- Signal saved to: `challenge_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 247.2ms
- Decoded bits: `01011000011010010010001110110111`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 3038.25 | 104.64 | `0` |
| 1 | 105.22 | 3021.30 | `1` |
| 2 | 3038.25 | 104.64 | `0` |
| 3 | 0.00 | 3125.92 | `1` |
| 4 | 105.22 | 3021.30 | `1` |
| 5 | 3143.45 | 0.00 | `0` |
| 6 | 3143.45 | 0.00 | `0` |
| 7 | 3143.45 | 0.00 | `0` |

### Test: challenge_30dB
- Input bits: `01011000011010010010001110110111`
- Bit count: 32
- SNR: 30 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 9.7ms
- Signal saved to: `challenge_30dB.npy`
- Max amplitude: 0.1069
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 233.0ms
- Decoded bits: `01011000011010010010001110110111`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2945.58 | 100.86 | `0` |
| 1 | 101.46 | 2933.56 | `1` |
| 2 | 2947.70 | 102.69 | `0` |
| 3 | 0.91 | 3033.78 | `1` |
| 4 | 100.39 | 2929.67 | `1` |
| 5 | 3051.23 | 0.72 | `0` |
| 6 | 3049.70 | 1.54 | `0` |
| 7 | 3049.10 | 0.35 | `0` |

### Test: challenge_20dB
- Input bits: `01011000011010010010001110110111`
- Bit count: 32
- SNR: 20 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 9.5ms
- Signal saved to: `challenge_20dB.npy`
- Max amplitude: 0.1234
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 221.5ms
- Decoded bits: `01011000011010010010001110110111`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2751.73 | 93.04 | `0` |
| 1 | 93.13 | 2731.20 | `1` |
| 2 | 2754.76 | 98.63 | `0` |
| 3 | 6.26 | 2834.74 | `1` |
| 4 | 93.20 | 2732.09 | `1` |
| 5 | 2839.52 | 3.92 | `0` |
| 6 | 2839.40 | 0.81 | `0` |
| 7 | 2847.72 | 8.85 | `0` |

### Test: challenge_10dB
- Input bits: `01011000011010010010001110110111`
- Bit count: 32
- SNR: 10 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 8.4ms
- Signal saved to: `challenge_10dB.npy`
- Max amplitude: 0.1829
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 221.0ms
- Decoded bits: `01011000011010010010001110110111`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2331.68 | 92.75 | `0` |
| 1 | 66.39 | 2313.89 | `1` |
| 2 | 2315.85 | 73.46 | `0` |
| 3 | 9.55 | 2395.71 | `1` |
| 4 | 80.57 | 2307.41 | `1` |
| 5 | 2401.90 | 14.16 | `0` |
| 6 | 2413.68 | 1.88 | `0` |
| 7 | 2399.25 | 18.75 | `0` |

## 3. Response Tests (64 bits)
Response bytes: `9674526284e58c35`

### Test: response_clean
- Input bits: `10010110011101000101001001100010...`
- Bit count: 64
- SNR: clean (no noise)
- Signal length: 500535 samples (11.350s)
- Encode time: 46.9ms
- Signal saved to: `response_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 444.1ms
- Decoded bits: `10010110011101000101001001100010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 104.71 | 3021.79 | `1` |
| 1 | 3038.76 | 104.15 | `0` |
| 2 | 3143.45 | 0.00 | `0` |
| 3 | 104.71 | 3021.79 | `1` |
| 4 | 3038.76 | 104.15 | `0` |
| 5 | 104.71 | 3021.79 | `1` |
| 6 | 0.00 | 3125.92 | `1` |
| 7 | 3038.76 | 104.15 | `0` |

### Test: response_30dB
- Input bits: `10010110011101000101001001100010...`
- Bit count: 64
- SNR: 30 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 42.7ms
- Signal saved to: `response_30dB.npy`
- Max amplitude: 0.1086
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 481.0ms
- Decoded bits: `10010110011101000101001001100010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 100.64 | 2928.62 | `1` |
| 1 | 2946.21 | 100.59 | `0` |
| 2 | 3047.20 | 0.47 | `0` |
| 3 | 98.38 | 2932.51 | `1` |
| 4 | 2947.17 | 102.10 | `0` |
| 5 | 101.88 | 2929.81 | `1` |
| 6 | 2.20 | 3031.81 | `1` |
| 7 | 2946.76 | 102.77 | `0` |

### Test: response_20dB
- Input bits: `10010110011101000101001001100010...`
- Bit count: 64
- SNR: 20 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 61.8ms
- Signal saved to: `response_20dB.npy`
- Max amplitude: 0.1260
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 431.1ms
- Decoded bits: `10010110011101000101001001100010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 95.67 | 2696.97 | `1` |
| 1 | 2801.42 | 4.06 | `0` |
| 2 | 2711.46 | 101.85 | `0` |
| 3 | 95.59 | 2698.87 | `1` |
| 4 | 2709.88 | 95.00 | `0` |
| 5 | 2.42 | 2783.89 | `1` |
| 6 | 92.19 | 2703.98 | `1` |
| 7 | 2803.54 | 5.07 | `0` |

### Test: response_10dB
- Input bits: `10010110011101000101001001100010...`
- Bit count: 64
- SNR: 10 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 39.2ms
- Signal saved to: `response_10dB.npy`
- Max amplitude: 0.1850
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 523.9ms
- Decoded bits: `10010110011101000101001001100010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 80.19 | 2278.40 | `1` |
| 1 | 2362.82 | 7.75 | `0` |
| 2 | 2287.12 | 79.38 | `0` |
| 3 | 87.31 | 2289.81 | `1` |
| 4 | 2281.90 | 85.22 | `0` |
| 5 | 16.14 | 2351.95 | `1` |
| 6 | 74.41 | 2277.47 | `1` |
| 7 | 2363.95 | 13.04 | `0` |

## 4. Full Crypto Round-Trip Test
Simulates complete laptopiPhonelaptop authentication:
- Challenge: `512aa257`
- Expected response: `7bcac81d9f57f29c`
- Decoded challenge: `512aa257`
- Challenge match: 
- Decoded response: `7bcac81d9f57f29c`
- HMAC verification:  PASS

## 5. Real Audio Simulation Tests
Simulates iPhone recording starting before signal arrives.
Pre-silence = time between iPhone starting to record and laptop starting to transmit.

Challenge bytes: `11919574`
Response bytes: `015f9c937555edbd`

### 5a. Sync pattern with pre-silence
Exact timing: laptop waits TONE_DURATION(1.0s) + 0.3s + sentinel(0.3s) = 1.6s

### Test: sync_pre_0.5s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 0.5s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 205065 samples (4.650s)
- Signal arrives at: 0.500s into recording
- Expected frame start: ~30869 samples (0.700s)
- Frame start found: sample 30495 (0.691s)
- Frame offset from expected: -374 samples
- Decode time: 182.3ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_pre_1.0s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 227115 samples (5.150s)
- Signal arrives at: 1.000s into recording
- Expected frame start: ~52920 samples (1.200s)
- Frame start found: sample 52545 (1.191s)
- Frame offset from expected: -375 samples
- Decode time: 202.3ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_pre_1.5s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.5s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 249165 samples (5.650s)
- Signal arrives at: 1.500s into recording
- Expected frame start: ~74970 samples (1.700s)
- Frame start found: sample 74595 (1.691s)
- Frame offset from expected: -375 samples
- Decode time: 234.9ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_pre_2.0s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 2.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 271215 samples (6.150s)
- Signal arrives at: 2.000s into recording
- Expected frame start: ~97020 samples (2.200s)
- Frame start found: sample 96645 (2.191s)
- Frame offset from expected: -375 samples
- Decode time: 155.5ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.3s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 240345 samples (5.450s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 65775 (1.491s)
- Frame offset from expected: -375 samples
- Decode time: 140.5ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.6s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 253575 samples (5.750s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79005 (1.791s)
- Frame offset from expected: -375 samples
- Decode time: 149.1ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.9s
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 266805 samples (6.050s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92235 (2.091s)
- Frame offset from expected: -375 samples
- Decode time: 132.0ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.3s_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 240345 samples (5.450s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 66525 (1.509s)
- Frame offset from expected: 375 samples
- Decode time: 127.2ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.6s_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 253575 samples (5.750s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79005 (1.791s)
- Frame offset from expected: -375 samples
- Decode time: 131.0ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### Test: sync_exact_1.9s_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 266805 samples (6.050s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92235 (2.091s)
- Frame offset from expected: -375 samples
- Decode time: 132.1ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### 5b. Challenge with pre-silence + noise
Exact timing: same as sync = 1.6s +- 0.3s

### Test: challenge_exact_1.3s
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 346185 samples (7.850s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 66525 (1.509s)
- Frame offset from expected: 375 samples
- Decode time: 254.9ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.6s
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 359415 samples (8.150s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79755 (1.809s)
- Frame offset from expected: 375 samples
- Decode time: 256.4ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.9s
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 372645 samples (8.450s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92985 (2.109s)
- Frame offset from expected: 375 samples
- Decode time: 419.4ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.3s_20dB
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 346185 samples (7.850s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 66525 (1.509s)
- Frame offset from expected: 375 samples
- Decode time: 403.6ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.6s_20dB
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 359415 samples (8.150s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79755 (1.809s)
- Frame offset from expected: 375 samples
- Decode time: 277.2ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.9s_20dB
- Input bits: `00010001100100011001010101110100`
- Bit count: 32
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 372645 samples (8.450s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92985 (2.109s)
- Frame offset from expected: 375 samples
- Decode time: 262.4ms
- Decoded bits: `00010001100100011001010101110100`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### 5c. Response with pre-silence + noise
Exact timing: laptop records immediately after challenge, response arrives ~0-1s later

### Test: response_exact_0.0s
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 0.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 500535 samples (11.350s)
- Signal arrives at: 0.000s into recording
- Expected frame start: ~8820 samples (0.200s)
- Frame start found: sample 9195 (0.209s)
- Frame offset from expected: 375 samples
- Decode time: 450.1ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.5s
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 0.5s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 522585 samples (11.850s)
- Signal arrives at: 0.500s into recording
- Expected frame start: ~30869 samples (0.700s)
- Frame start found: sample 31245 (0.709s)
- Frame offset from expected: 376 samples
- Decode time: 426.3ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_1.0s
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 1.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 544635 samples (12.350s)
- Signal arrives at: 1.000s into recording
- Expected frame start: ~52920 samples (1.200s)
- Frame start found: sample 53295 (1.209s)
- Frame offset from expected: 375 samples
- Decode time: 403.1ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.0s_20dB
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 0.0s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 500535 samples (11.350s)
- Signal arrives at: 0.000s into recording
- Expected frame start: ~8820 samples (0.200s)
- Frame start found: sample 9195 (0.209s)
- Frame offset from expected: 375 samples
- Decode time: 504.2ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.5s_20dB
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 0.5s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 522585 samples (11.850s)
- Signal arrives at: 0.500s into recording
- Expected frame start: ~30869 samples (0.700s)
- Frame start found: sample 31245 (0.709s)
- Frame offset from expected: 376 samples
- Decode time: 586.8ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_1.0s_20dB
- Input bits: `00000001010111111001110010010011...`
- Bit count: 64
- Pre-silence: 1.0s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 544635 samples (12.350s)
- Signal arrives at: 1.000s into recording
- Expected frame start: ~52920 samples (1.200s)
- Frame start found: sample 53295 (1.209s)
- Frame offset from expected: 375 samples
- Decode time: 441.4ms
- Decoded bits: `00000001010111111001110010010011...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

## Summary
| Test | Result |
|------|--------|
| sync_clean |  PASS |
| sync_30dB |  PASS |
| sync_20dB |  PASS |
| sync_10dB |  PASS |
| challenge_clean |  PASS |
| challenge_30dB |  PASS |
| challenge_20dB |  PASS |
| challenge_10dB |  PASS |
| response_clean |  PASS |
| response_30dB |  PASS |
| response_20dB |  PASS |
| response_10dB |  PASS |
| crypto_roundtrip |  PASS |
| sync_presilence_0.5s |  PASS |
| sync_presilence_1.0s |  PASS |
| sync_presilence_1.5s |  PASS |
| sync_presilence_2.0s |  PASS |
| sync_exact_1.3s |  PASS |
| sync_exact_1.6s |  PASS |
| sync_exact_1.9s |  PASS |
| sync_exact_1.3s_20dB |  PASS |
| sync_exact_1.6s_20dB |  PASS |
| sync_exact_1.9s_20dB |  PASS |
| challenge_exact_1.3s |  PASS |
| challenge_exact_1.6s |  PASS |
| challenge_exact_1.9s |  PASS |
| challenge_exact_1.3s_20dB |  PASS |
| challenge_exact_1.6s_20dB |  PASS |
| challenge_exact_1.9s_20dB |  PASS |
| response_exact_0.0s |  PASS |
| response_exact_0.5s |  PASS |
| response_exact_1.0s |  PASS |
| response_exact_0.0s_20dB |  PASS |
| response_exact_0.5s_20dB |  PASS |
| response_exact_1.0s_20dB |  PASS |

**35/35 tests passed**

 All signal processing tests passed  FSK pipeline is working correctly.