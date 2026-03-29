# FSK Signal Processing Test Report
Generated: 2026-03-29 19:30:09

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
- Encode time: 4.9ms
- Signal saved to: `sync_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 166.9ms
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
- Max amplitude: 0.1076
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 115.5ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 102.45 | 2941.73 | `1` |
| 1 | 2956.30 | 99.17 | `0` |
| 2 | 102.22 | 2941.57 | `1` |
| 3 | 2957.61 | 100.75 | `0` |
| 4 | 101.08 | 2941.51 | `1` |
| 5 | 2956.35 | 101.45 | `0` |
| 6 | 101.78 | 2940.80 | `1` |
| 7 | 2957.83 | 100.38 | `0` |

### Test: sync_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 20 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 4.2ms
- Signal saved to: `sync_20dB.npy`
- Max amplitude: 0.1229
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 116.5ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 97.33 | 2749.47 | `1` |
| 1 | 2766.79 | 96.24 | `0` |
| 2 | 93.72 | 2744.38 | `1` |
| 3 | 2760.51 | 93.26 | `0` |
| 4 | 97.11 | 2752.92 | `1` |
| 5 | 2760.85 | 96.04 | `0` |
| 6 | 102.39 | 2745.73 | `1` |
| 7 | 2761.22 | 90.40 | `0` |

### Test: sync_10dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 10 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 5.0ms
- Signal saved to: `sync_10dB.npy`
- Max amplitude: 0.1744
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 105.4ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 82.87 | 2339.29 | `1` |
| 1 | 2356.74 | 70.74 | `0` |
| 2 | 80.41 | 2348.03 | `1` |
| 3 | 2371.92 | 94.32 | `0` |
| 4 | 71.67 | 2353.42 | `1` |
| 5 | 2353.75 | 85.37 | `0` |
| 6 | 76.41 | 2360.78 | `1` |
| 7 | 2358.93 | 75.65 | `0` |

## 2. Challenge Tests (32 bits)
Challenge bytes: `47a6d980`

### Test: challenge_clean
- Input bits: `01000111101001101101100110000000`
- Bit count: 32
- SNR: clean (no noise)
- Signal length: 288855 samples (6.550s)
- Encode time: 6.6ms
- Signal saved to: `challenge_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 223.5ms
- Decoded bits: `01000111101001101101100110000000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 3038.25 | 104.64 | `0` |
| 1 | 105.22 | 3021.30 | `1` |
| 2 | 3143.45 | 0.00 | `0` |
| 3 | 3143.45 | 0.00 | `0` |
| 4 | 3038.25 | 104.64 | `0` |
| 5 | 0.00 | 3125.92 | `1` |
| 6 | 0.00 | 3125.92 | `1` |
| 7 | 0.00 | 3125.92 | `1` |

### Test: challenge_30dB
- Input bits: `01000111101001101101100110000000`
- Bit count: 32
- SNR: 30 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 7.6ms
- Signal saved to: `challenge_30dB.npy`
- Max amplitude: 0.1093
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 202.2ms
- Decoded bits: `01000111101001101101100110000000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2959.29 | 104.24 | `0` |
| 1 | 101.87 | 2939.43 | `1` |
| 2 | 3058.09 | 1.58 | `0` |
| 3 | 3058.12 | 1.18 | `0` |
| 4 | 2955.71 | 101.39 | `0` |
| 5 | 0.67 | 3041.79 | `1` |
| 6 | 1.84 | 3041.16 | `1` |
| 7 | 0.92 | 3041.14 | `1` |

### Test: challenge_20dB
- Input bits: `01000111101001101101100110000000`
- Bit count: 32
- SNR: 20 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 8.4ms
- Signal saved to: `challenge_20dB.npy`
- Max amplitude: 0.1270
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 218.6ms
- Decoded bits: `01000111101001101101100110000000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2770.57 | 91.73 | `0` |
| 1 | 93.75 | 2751.62 | `1` |
| 2 | 2864.00 | 0.81 | `0` |
| 3 | 2862.56 | 7.47 | `0` |
| 4 | 2770.97 | 92.79 | `0` |
| 5 | 1.22 | 2855.83 | `1` |
| 6 | 4.22 | 2852.37 | `1` |
| 7 | 9.78 | 2851.71 | `1` |

### Test: challenge_10dB
- Input bits: `01000111101001101101100110000000`
- Bit count: 32
- SNR: 10 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 9.6ms
- Signal saved to: `challenge_10dB.npy`
- Max amplitude: 0.1964
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 246.9ms
- Decoded bits: `01000111101001101101100110000000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2293.95 | 76.31 | `0` |
| 1 | 82.77 | 2273.89 | `1` |
| 2 | 2366.72 | 7.11 | `0` |
| 3 | 2366.36 | 10.65 | `0` |
| 4 | 2292.86 | 83.26 | `0` |
| 5 | 12.37 | 2355.58 | `1` |
| 6 | 13.22 | 2353.42 | `1` |
| 7 | 11.70 | 2351.70 | `1` |

## 3. Response Tests (64 bits)
Response bytes: `84f014ba4810b711`

### Test: response_clean
- Input bits: `10000100111100000001010010111010...`
- Bit count: 64
- SNR: clean (no noise)
- Signal length: 500535 samples (11.350s)
- Encode time: 40.0ms
- Signal saved to: `response_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 374.3ms
- Decoded bits: `10000100111100000001010010111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 104.71 | 3021.79 | `1` |
| 1 | 3038.76 | 104.15 | `0` |
| 2 | 3143.45 | 0.00 | `0` |
| 3 | 3143.45 | 0.00 | `0` |
| 4 | 3143.45 | 0.00 | `0` |
| 5 | 104.71 | 3021.79 | `1` |
| 6 | 3038.76 | 104.15 | `0` |
| 7 | 3143.45 | 0.00 | `0` |

### Test: response_30dB
- Input bits: `10000100111100000001010010111010...`
- Bit count: 64
- SNR: 30 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 47.4ms
- Signal saved to: `response_30dB.npy`
- Max amplitude: 0.1081
- Frame start: sample 8445 (0.191s)
- Data start: sample 54750 (1.241s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: -375 samples
- Decode time: 373.3ms
- Decoded bits: `10000100111100000001010010111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 99.72 | 2906.21 | `1` |
| 1 | 2924.77 | 100.44 | `0` |
| 2 | 3023.95 | 1.26 | `0` |
| 3 | 3023.52 | 3.12 | `0` |
| 4 | 3023.51 | 1.60 | `0` |
| 5 | 101.33 | 2907.02 | `1` |
| 6 | 2923.07 | 99.84 | `0` |
| 7 | 3024.23 | 2.43 | `0` |

### Test: response_20dB
- Input bits: `10000100111100000001010010111010...`
- Bit count: 64
- SNR: 20 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 28.8ms
- Signal saved to: `response_20dB.npy`
- Max amplitude: 0.1268
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 335.7ms
- Decoded bits: `10000100111100000001010010111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 97.38 | 2724.42 | `1` |
| 1 | 2839.81 | 7.05 | `0` |
| 2 | 2833.83 | 3.48 | `0` |
| 3 | 2837.97 | 4.55 | `0` |
| 4 | 2743.20 | 98.22 | `0` |
| 5 | 97.93 | 2724.79 | `1` |
| 6 | 2834.00 | 3.79 | `0` |
| 7 | 2740.46 | 99.80 | `0` |

### Test: response_10dB
- Input bits: `10000100111100000001010010111010...`
- Bit count: 64
- SNR: 10 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 36.1ms
- Signal saved to: `response_10dB.npy`
- Max amplitude: 0.1869
- Frame start: sample 9195 (0.209s)
- Data start: sample 55500 (1.259s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 375 samples
- Decode time: 350.8ms
- Decoded bits: `10000100111100000001010010111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 75.91 | 2247.30 | `1` |
| 1 | 2349.31 | 8.50 | `0` |
| 2 | 2347.66 | 15.06 | `0` |
| 3 | 2348.55 | 8.12 | `0` |
| 4 | 2278.78 | 69.39 | `0` |
| 5 | 62.12 | 2258.55 | `1` |
| 6 | 2345.27 | 5.60 | `0` |
| 7 | 2275.96 | 75.59 | `0` |

## 4. Full Crypto Round-Trip Test
Simulates complete laptopiPhonelaptop authentication:
- Challenge: `8d03b51f`
- Expected response: `d1bac4f732e13bcf`
- Decoded challenge: `8d03b51f`
- Challenge match: 
- Decoded response: `d1bac4f732e13bcf`
- HMAC verification:  PASS

## 5. Real Audio Simulation Tests
Simulates iPhone recording starting before signal arrives.
Pre-silence = time between iPhone starting to record and laptop starting to transmit.

Challenge bytes: `8fdd8ec5`
Response bytes: `4eddfffa4017c1df`

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
- Decode time: 108.5ms
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
- Decode time: 123.7ms
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
- Decode time: 129.5ms
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
- Decode time: 130.0ms
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
- Decode time: 125.9ms
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
- Decode time: 118.9ms
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
- Decode time: 125.8ms
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
- Frame start found: sample 65775 (1.491s)
- Frame offset from expected: -375 samples
- Decode time: 112.7ms
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
- Frame start found: sample 79755 (1.809s)
- Frame offset from expected: 375 samples
- Decode time: 110.9ms
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
- Decode time: 123.1ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

### 5b. Challenge with pre-silence + noise
Exact timing: same as sync = 1.6s +- 0.3s

### Test: challenge_exact_1.3s
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 346185 samples (7.850s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 65775 (1.491s)
- Frame offset from expected: -375 samples
- Decode time: 198.8ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.6s
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 359415 samples (8.150s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79005 (1.791s)
- Frame offset from expected: -375 samples
- Decode time: 180.6ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.9s
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 372645 samples (8.450s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92235 (2.091s)
- Frame offset from expected: -375 samples
- Decode time: 192.1ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.3s_20dB
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.3s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 346185 samples (7.850s)
- Signal arrives at: 1.300s into recording
- Expected frame start: ~66150 samples (1.500s)
- Frame start found: sample 66525 (1.509s)
- Frame offset from expected: 375 samples
- Decode time: 195.5ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.6s_20dB
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.6s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 359415 samples (8.150s)
- Signal arrives at: 1.600s into recording
- Expected frame start: ~79380 samples (1.800s)
- Frame start found: sample 79005 (1.791s)
- Frame offset from expected: -375 samples
- Decode time: 193.8ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### Test: challenge_exact_1.9s_20dB
- Input bits: `10001111110111011000111011000101`
- Bit count: 32
- Pre-silence: 1.9s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 372645 samples (8.450s)
- Signal arrives at: 1.900s into recording
- Expected frame start: ~92610 samples (2.100s)
- Frame start found: sample 92235 (2.091s)
- Frame offset from expected: -375 samples
- Decode time: 206.7ms
- Decoded bits: `10001111110111011000111011000101`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

### 5c. Response with pre-silence + noise
Exact timing: laptop records immediately after challenge, response arrives ~0-1s later

### Test: response_exact_0.0s
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 0.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 500535 samples (11.350s)
- Signal arrives at: 0.000s into recording
- Expected frame start: ~8820 samples (0.200s)
- Frame start found: sample 9195 (0.209s)
- Frame offset from expected: 375 samples
- Decode time: 523.4ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.5s
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 0.5s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 522585 samples (11.850s)
- Signal arrives at: 0.500s into recording
- Expected frame start: ~30869 samples (0.700s)
- Frame start found: sample 31245 (0.709s)
- Frame offset from expected: 376 samples
- Decode time: 396.3ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_1.0s
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 1.0s (simulates recording starting before signal)
- SNR: clean (no noise)
- Total signal length: 544635 samples (12.350s)
- Signal arrives at: 1.000s into recording
- Expected frame start: ~52920 samples (1.200s)
- Frame start found: sample 53295 (1.209s)
- Frame offset from expected: 375 samples
- Decode time: 390.7ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.0s_20dB
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 0.0s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 500535 samples (11.350s)
- Signal arrives at: 0.000s into recording
- Expected frame start: ~8820 samples (0.200s)
- Frame start found: sample 9195 (0.209s)
- Frame offset from expected: 375 samples
- Decode time: 364.3ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_0.5s_20dB
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 0.5s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 522585 samples (11.850s)
- Signal arrives at: 0.500s into recording
- Expected frame start: ~30869 samples (0.700s)
- Frame start found: sample 31245 (0.709s)
- Frame offset from expected: 376 samples
- Decode time: 349.4ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

### Test: response_exact_1.0s_20dB
- Input bits: `01001110110111011111111111111010...`
- Bit count: 64
- Pre-silence: 1.0s (simulates recording starting before signal)
- SNR: 20 dB
- Total signal length: 544635 samples (12.350s)
- Signal arrives at: 1.000s into recording
- Expected frame start: ~52920 samples (1.200s)
- Frame start found: sample 53295 (1.209s)
- Frame offset from expected: 375 samples
- Decode time: 336.1ms
- Decoded bits: `01001110110111011111111111111010...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

## 6. Decode Timing Breakdown
Measures time for each decode stage to identify bottleneck.
iPhone ACK timeout is 5s — total decode must be under that.

### Timing Test: sync_1.6s_presilence
- Bit count: 16, Pre-silence: 1.6s, SNR: clean
| Stage | Time |
|-------|------|
| Bandpass filter | 23.4ms |
| Barker sync | 15.4ms |
| Goertzel demod | 61.1ms |
| **Total** | **100.0ms** |
- Frame start: sample 79005 (1.791s)
- Bit errors: 0/16
- Result: PASS

### Timing Test: challenge_1.6s_presilence
- Bit count: 32, Pre-silence: 1.6s, SNR: clean
| Stage | Time |
|-------|------|
| Bandpass filter | 13.1ms |
| Barker sync | 18.3ms |
| Goertzel demod | 157.9ms |
| **Total** | **189.2ms** |
- Frame start: sample 79005 (1.791s)
- Bit errors: 0/32
- Result: PASS

### Timing Test: response_0.5s_presilence
- Bit count: 64, Pre-silence: 0.5s, SNR: clean
| Stage | Time |
|-------|------|
| Bandpass filter | 16.8ms |
| Barker sync | 12.2ms |
| Goertzel demod | 344.8ms |
| **Total** | **373.8ms** |
- Frame start: sample 31245 (0.709s)
- Bit errors: 0/64
- Result: PASS

### Timing Test: sync_1.6s_20dB
- Bit count: 16, Pre-silence: 1.6s, SNR: 20dB
| Stage | Time |
|-------|------|
| Bandpass filter | 11.0ms |
| Barker sync | 20.9ms |
| Goertzel demod | 96.5ms |
| **Total** | **128.5ms** |
- Frame start: sample 79005 (1.791s)
- Bit errors: 0/16
- Result: PASS

### Timing Test: challenge_1.6s_20dB
- Bit count: 32, Pre-silence: 1.6s, SNR: 20dB
| Stage | Time |
|-------|------|
| Bandpass filter | 18.9ms |
| Barker sync | 19.9ms |
| Goertzel demod | 187.7ms |
| **Total** | **226.4ms** |
- Frame start: sample 79005 (1.791s)
- Bit errors: 0/32
- Result: PASS

### Timing Test: response_0.5s_20dB
- Bit count: 64, Pre-silence: 0.5s, SNR: 20dB
| Stage | Time |
|-------|------|
| Bandpass filter | 28.6ms |
| Barker sync | 19.5ms |
| Goertzel demod | 342.6ms |
| **Total** | **390.8ms** |
- Frame start: sample 31245 (0.709s)
- Bit errors: 0/64
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
| timing_sync_1.6s |  PASS |
| timing_challenge_1.6s |  PASS |
| timing_response_0.5s |  PASS |
| timing_sync_1.6s_20dB |  PASS |
| timing_challenge_1.6s_20dB |  PASS |
| timing_response_0.5s_20dB |  PASS |

**41/41 tests passed**

 All signal processing tests passed  FSK pipeline is working correctly.