# FSK Signal Processing Test Report
Generated: 2026-03-29 19:05:56

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
- Encode time: 6.4ms
- Signal saved to: `sync_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 178.2ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 0.00 | 3125.92 | `1` |
| 1 | 3143.45 | 0.01 | `0` |
| 2 | 0.00 | 3125.92 | `1` |
| 3 | 3143.45 | 0.01 | `0` |
| 4 | 0.00 | 3125.92 | `1` |
| 5 | 3143.45 | 0.01 | `0` |
| 6 | 0.00 | 3125.92 | `1` |
| 7 | 3143.45 | 0.01 | `0` |

### Test: sync_30dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 30 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 1.5ms
- Signal saved to: `sync_30dB.npy`
- Max amplitude: 0.1072
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 196.8ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2.51 | 3031.38 | `1` |
| 1 | 3048.61 | 1.79 | `0` |
| 2 | 1.29 | 3030.21 | `1` |
| 3 | 3047.94 | 1.23 | `0` |
| 4 | 1.97 | 3030.70 | `1` |
| 5 | 3047.21 | 1.30 | `0` |
| 6 | 1.22 | 3032.09 | `1` |
| 7 | 3049.02 | 0.11 | `0` |

### Test: sync_20dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 20 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 0.0ms
- Signal saved to: `sync_20dB.npy`
- Max amplitude: 0.1237
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 184.1ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 3.06 | 2829.32 | `1` |
| 1 | 2846.70 | 6.18 | `0` |
| 2 | 4.43 | 2830.09 | `1` |
| 3 | 2847.57 | 2.78 | `0` |
| 4 | 9.14 | 2831.22 | `1` |
| 5 | 2850.34 | 3.90 | `0` |
| 6 | 1.87 | 2827.40 | `1` |
| 7 | 2850.82 | 5.11 | `0` |

### Test: sync_10dB
- Input bits: `1010101010101010`
- Bit count: 16
- SNR: 10 dB
- Signal length: 183015 samples (4.150s)
- Encode time: 0.0ms
- Signal saved to: `sync_10dB.npy`
- Max amplitude: 0.1830
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 181.8ms
- Decoded bits: `1010101010101010`
- Bit errors: 0/16 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 18.55 | 2381.02 | `1` |
| 1 | 2377.54 | 11.42 | `0` |
| 2 | 17.45 | 2366.09 | `1` |
| 3 | 2391.47 | 8.05 | `0` |
| 4 | 17.79 | 2363.78 | `1` |
| 5 | 2376.14 | 14.81 | `0` |
| 6 | 8.09 | 2374.78 | `1` |
| 7 | 2389.42 | 13.54 | `0` |

## 2. Challenge Tests (32 bits)
Challenge bytes: `8b615330`

### Test: challenge_clean
- Input bits: `10001011011000010101001100110000`
- Bit count: 32
- SNR: clean (no noise)
- Signal length: 288855 samples (6.550s)
- Encode time: 17.6ms
- Signal saved to: `challenge_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 285.1ms
- Decoded bits: `10001011011000010101001100110000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 0.00 | 3125.92 | `1` |
| 1 | 3143.45 | 0.01 | `0` |
| 2 | 3143.45 | 0.00 | `0` |
| 3 | 3143.45 | 0.01 | `0` |
| 4 | 0.00 | 3125.92 | `1` |
| 5 | 3143.45 | 0.01 | `0` |
| 6 | 0.01 | 3125.92 | `1` |
| 7 | 0.01 | 3125.92 | `1` |

### Test: challenge_30dB
- Input bits: `10001011011000010101001100110000`
- Bit count: 32
- SNR: 30 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 9.1ms
- Signal saved to: `challenge_30dB.npy`
- Max amplitude: 0.1086
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 279.6ms
- Decoded bits: `10001011011000010101001100110000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 1.46 | 3036.19 | `1` |
| 1 | 3056.51 | 1.52 | `0` |
| 2 | 3056.90 | 1.21 | `0` |
| 3 | 3056.43 | 1.59 | `0` |
| 4 | 1.97 | 3038.72 | `1` |
| 5 | 3055.01 | 1.24 | `0` |
| 6 | 0.54 | 3039.57 | `1` |
| 7 | 1.21 | 3038.05 | `1` |

### Test: challenge_20dB
- Input bits: `10001011011000010101001100110000`
- Bit count: 32
- SNR: 20 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 0.0ms
- Signal saved to: `challenge_20dB.npy`
- Max amplitude: 0.1280
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 280.0ms
- Decoded bits: `10001011011000010101001100110000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 2.42 | 2845.40 | `1` |
| 1 | 2863.04 | 9.32 | `0` |
| 2 | 2854.06 | 6.08 | `0` |
| 3 | 2859.29 | 4.72 | `0` |
| 4 | 4.57 | 2845.56 | `1` |
| 5 | 2865.07 | 3.65 | `0` |
| 6 | 2.15 | 2843.38 | `1` |
| 7 | 3.70 | 2849.89 | `1` |

### Test: challenge_10dB
- Input bits: `10001011011000010101001100110000`
- Bit count: 32
- SNR: 10 dB
- Signal length: 288855 samples (6.550s)
- Encode time: 4.9ms
- Signal saved to: `challenge_10dB.npy`
- Max amplitude: 0.1809
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 299.6ms
- Decoded bits: `10001011011000010101001100110000`
- Bit errors: 0/32 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 3.37 | 2332.66 | `1` |
| 1 | 2334.13 | 5.18 | `0` |
| 2 | 2353.99 | 9.97 | `0` |
| 3 | 2349.55 | 8.53 | `0` |
| 4 | 1.45 | 2338.96 | `1` |
| 5 | 2359.79 | 14.18 | `0` |
| 6 | 7.69 | 2350.59 | `1` |
| 7 | 22.38 | 2343.53 | `1` |

## 3. Response Tests (64 bits)
Response bytes: `8452474e27f3b257`

### Test: response_clean
- Input bits: `10000100010100100100011101001110...`
- Bit count: 64
- SNR: clean (no noise)
- Signal length: 500535 samples (11.350s)
- Encode time: 66.4ms
- Signal saved to: `response_clean.npy`
- Max amplitude: 0.1000
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 728.0ms
- Decoded bits: `10000100010100100100011101001110...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 0.00 | 3125.92 | `1` |
| 1 | 3143.45 | 0.01 | `0` |
| 2 | 3143.45 | 0.00 | `0` |
| 3 | 3143.45 | 0.00 | `0` |
| 4 | 3143.45 | 0.01 | `0` |
| 5 | 0.00 | 3125.92 | `1` |
| 6 | 3143.45 | 0.01 | `0` |
| 7 | 3143.45 | 0.00 | `0` |

### Test: response_30dB
- Input bits: `10000100010100100100011101001110...`
- Bit count: 64
- SNR: 30 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 59.2ms
- Signal saved to: `response_30dB.npy`
- Max amplitude: 0.1080
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 502.1ms
- Decoded bits: `10000100010100100100011101001110...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 1.07 | 3020.02 | `1` |
| 1 | 3036.13 | 1.37 | `0` |
| 2 | 3037.71 | 0.63 | `0` |
| 3 | 3036.12 | 0.96 | `0` |
| 4 | 3036.12 | 1.78 | `0` |
| 5 | 2.06 | 3019.81 | `1` |
| 6 | 3038.64 | 1.49 | `0` |
| 7 | 3037.14 | 0.84 | `0` |

### Test: response_20dB
- Input bits: `10000100010100100100011101001110...`
- Bit count: 64
- SNR: 20 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 45.5ms
- Signal saved to: `response_20dB.npy`
- Max amplitude: 0.1253
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 464.0ms
- Decoded bits: `10000100010100100100011101001110...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 4.09 | 2832.70 | `1` |
| 1 | 2849.54 | 8.40 | `0` |
| 2 | 2857.65 | 2.85 | `0` |
| 3 | 2857.63 | 2.31 | `0` |
| 4 | 2858.23 | 0.99 | `0` |
| 5 | 4.71 | 2838.90 | `1` |
| 6 | 2852.62 | 2.23 | `0` |
| 7 | 2855.21 | 7.68 | `0` |

### Test: response_10dB
- Input bits: `10000100010100100100011101001110...`
- Bit count: 64
- SNR: 10 dB
- Signal length: 500535 samples (11.350s)
- Encode time: 47.7ms
- Signal saved to: `response_10dB.npy`
- Max amplitude: 0.1925
- Frame start: sample 8820 (0.200s)
- Data start: sample 55125 (1.250s)
- Expected frame start: ~8820 samples (0.200s)
- Frame offset from expected: 0 samples
- Decode time: 648.6ms
- Decoded bits: `10000100010100100100011101001110...`
- Bit errors: 0/64 (BER=0.0%)
- Result: PASS

**Symbol power samples (first 8 bits):**
| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |
|-----|-----------|-----------|---------|
| 0 | 3.76 | 2273.64 | `1` |
| 1 | 2273.55 | 12.94 | `0` |
| 2 | 2269.77 | 26.28 | `0` |
| 3 | 2275.78 | 12.31 | `0` |
| 4 | 2272.05 | 12.83 | `0` |
| 5 | 11.59 | 2265.07 | `1` |
| 6 | 2270.97 | 14.70 | `0` |
| 7 | 2275.69 | 2.59 | `0` |

## 4. Full Crypto Round-Trip Test
Simulates complete laptopiPhonelaptop authentication:
- Challenge: `a34c50dd`
- Expected response: `764ccd3ec29fc8b4`
- Decoded challenge: `a34c50dd`
- Challenge match: 
- Decoded response: `764ccd3ec29fc8b4`
- HMAC verification:  PASS

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

**13/13 tests passed**

 All signal processing tests passed  FSK pipeline is working correctly.