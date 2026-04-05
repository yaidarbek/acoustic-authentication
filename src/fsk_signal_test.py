"""
fsk_signal_test.py
Tests the full FSK signal processing pipeline without audio hardware.
Encodes signals to numpy arrays, saves to files, decodes and verifies.
Outputs detailed markdown report to fsk_test_report.md
"""

import sys
import os
import time
import numpy as np
from scipy.signal import butter, filtfilt
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from working_fsk import WorkingFSK
from crypto_core import CryptographicCore

SHARED_KEY   = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0')
SYNC_PATTERN = '1010101010101010'
REPORT_FILE  = os.path.join(os.path.dirname(__file__), 'fsk_test_report.md')
SIGNAL_DIR   = os.path.join(os.path.dirname(__file__), 'sim_channel')

lines = []  # markdown lines

def md(text=''):
    lines.append(text)
    print(text, flush=True)

def md_code(text):
    lines.append(f'```\n{text}\n```')
    print(text, flush=True)

def save_report():
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n Report saved to: {REPORT_FILE}', flush=True)

#  FSK Engine (no audio) 

class FSKEngine:
    """WorkingFSK without PyAudio  pure signal processing"""

    def __init__(self):
        self.sample_rate    = 44100
        self.f0             = 7000   # bit 0
        self.f1             = 9000   # bit 1
        self.symbol_duration = 0.15  # 150ms
        self.amplitude      = 0.1
        self.guard_duration = 0.2    # 200ms guard interval

    @property
    def samples_per_symbol(self):
        return int(self.sample_rate * self.symbol_duration)

    def generate_tone(self, frequency, duration):
        samples  = int(self.sample_rate * duration)
        t        = np.linspace(0, duration, samples, False)
        wave     = self.amplitude * np.sin(2 * np.pi * frequency * t)
        fade_len = int(samples * 0.05)
        if fade_len > 0:
            wave[:fade_len]  *= np.linspace(0, 1, fade_len)
            wave[-fade_len:] *= np.linspace(1, 0, fade_len)
        return wave.astype(np.float32)

    def encode(self, bits: str) -> np.ndarray:
        """Encode bits to FSK signal with guard interval + Barker-7 preamble + tail silence"""
        barker        = [1, 1, 1, -1, -1, 1, -1]
        preamble_bits = ''.join('1' if c == 1 else '0' for c in barker)
        full_data     = preamble_bits + bits

        # Guard interval silence before preamble
        guard  = np.zeros(int(self.sample_rate * self.guard_duration), dtype=np.float32)
        signal = guard.copy()

        for bit in full_data:
            freq   = self.f1 if bit == '1' else self.f0
            signal = np.concatenate([signal, self.generate_tone(freq, self.symbol_duration)])

        # Tail silence — ensures last symbol is fully captured after Barker offset
        tail   = np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)
        signal = np.concatenate([signal, tail])

        return signal

    def add_noise(self, signal: np.ndarray, snr_db: float) -> np.ndarray:
        """Add Gaussian noise at specified SNR"""
        signal_power = np.mean(signal ** 2)
        noise_power  = signal_power / (10 ** (snr_db / 10))
        noise        = np.random.normal(0, np.sqrt(noise_power), len(signal)).astype(np.float32)
        return signal + noise

    def bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        nyq  = self.sample_rate / 2
        b, a = butter(4, [6000/nyq, 10000/nyq], btype='band')
        return filtfilt(b, a, signal).astype(np.float32)

    def apply_agc_windowed(self, signal: np.ndarray, frame_start: int, expected_bits: int) -> tuple:
        """Apply AGC only to the detected signal window"""
        window_start = max(0, frame_start)
        # Use full remaining signal from frame_start — never clip short
        window_end   = len(signal)
        window       = signal[window_start:window_end]
        max_amp      = np.max(np.abs(window))
        if max_amp > 0:
            window = (window / max_amp).astype(np.float32)
        return window, window_start

    def barker_sync(self, signal: np.ndarray) -> int:
        barker = [1, 1, 1, -1, -1, 1, -1]

        # Build reference using same tone generation as encoder (with fade)
        # This ensures correlation matches actual signal shape
        ref_signal = np.array([], dtype=np.float32)
        for chip in barker:
            freq = self.f1 if chip > 0 else self.f0
            ref_signal = np.concatenate([ref_signal, self.generate_tone(freq, self.symbol_duration)])
        reference = ref_signal

        if len(signal) < len(reference):
            return 0

        # Limit search to first 15s to cover worst-case ACK + sleep delay
        search_end    = min(len(signal) - len(reference), int(self.sample_rate * 15.0))
        search_signal = signal[:search_end + len(reference)]

        # Step 1: Coarse search on consistently downsampled signal
        ds     = 10
        sig_ds = search_signal[::ds]
        ref_ds = reference[::ds]
        corr   = np.correlate(sig_ds, ref_ds, mode='valid')
        coarse_peak = int(np.argmax(np.abs(corr))) * ds

        # Step 2: Fine search every 10 samples within +-1 symbol around coarse peak
        fine_start = max(0, coarse_peak - self.samples_per_symbol)
        fine_end   = min(len(signal) - len(reference), coarse_peak + self.samples_per_symbol)
        max_corr   = 0.0
        fine_peak  = coarse_peak
        for i in range(fine_start, fine_end, 10):
            s = float(np.abs(np.dot(signal[i:i+len(reference)], reference)))
            if s > max_corr:
                max_corr  = s
                fine_peak = i

        # Step 3: Ultra-fine search every 1 sample within +-10 samples of fine peak
        ultra_start = max(0, fine_peak - 10)
        ultra_end   = min(len(signal) - len(reference), fine_peak + 10)
        for i in range(ultra_start, ultra_end):
            s = float(np.abs(np.dot(signal[i:i+len(reference)], reference)))
            if s > max_corr:
                max_corr  = s
                fine_peak = i

        print(f'Barker sync: coarse={coarse_peak} fine={fine_peak}')
        return fine_peak

    def goertzel(self, samples: np.ndarray, freq: float) -> float:
        N      = len(samples)
        k      = int(0.5 + (N * freq / self.sample_rate))
        w      = (2.0 * np.pi / N) * k
        cosine = np.cos(w)
        coeff  = 2.0 * cosine
        q0 = q1 = q2 = 0.0
        for s in samples:
            q0 = coeff * q1 - q2 + s
            q2 = q1
            q1 = q0
        real = q1 - q2 * cosine
        imag = q2 * np.sin(w)
        return float(np.sqrt(real*real + imag*imag))

    def decode(self, signal: np.ndarray, expected_bits: int) -> dict:
        """Full decode pipeline, returns detailed stats"""
        stats = {
            'expected_bits': expected_bits,
            'decoded_bits':  '',
            'max_amplitude': float(np.max(np.abs(signal))),
            'frame_start':   0,
            'data_start':    0,
            'symbol_powers': [],
            'errors':        []
        }

        # Quality check
        if stats['max_amplitude'] < 0.01:
            stats['errors'].append(f'Signal too weak: {stats["max_amplitude"]:.4f}')
            return stats

        # Bandpass filter
        filtered = self.bandpass_filter(signal)

        # Barker sync on raw signal
        frame_start = self.barker_sync(filtered)
        data_start  = frame_start + 7 * self.samples_per_symbol
        stats['frame_start'] = frame_start
        stats['data_start']  = data_start

        # Windowed AGC
        window, window_start = self.apply_agc_windowed(filtered, frame_start, expected_bits)
        windowed_data_start  = data_start - window_start

        # Goertzel demodulation
        decoded_bits = ''
        for i in range(expected_bits):
            sym_start = windowed_data_start + i * self.samples_per_symbol
            sym_end   = sym_start + self.samples_per_symbol
            if sym_end > len(window):
                stats['errors'].append(f'Ran out of samples at bit {i}')
                break
            sym_data = window[sym_start:sym_end]
            p0 = self.goertzel(sym_data, self.f0)
            p1 = self.goertzel(sym_data, self.f1)
            bit = '1' if p1 > p0 else '0'
            decoded_bits += bit
            stats['symbol_powers'].append({'bit': i, 'p0': p0, 'p1': p1, 'decoded': bit})

        stats['decoded_bits'] = decoded_bits
        return stats


#  Test Runner 

def run_test(fsk: FSKEngine, name: str, bits: str, snr_db: float = None) -> bool:
    md(f'\n### Test: {name}')
    md(f'- Input bits: `{bits[:32]}{"..." if len(bits)>32 else ""}`')
    md(f'- Bit count: {len(bits)}')
    md(f'- SNR: {"clean (no noise)" if snr_db is None else f"{snr_db} dB"}')

    # Encode
    t0     = time.time()
    signal = fsk.encode(bits)
    encode_time = time.time() - t0
    md(f'- Signal length: {len(signal)} samples ({len(signal)/fsk.sample_rate:.3f}s)')
    md(f'- Encode time: {encode_time*1000:.1f}ms')

    # Add noise if requested
    if snr_db is not None:
        signal = fsk.add_noise(signal, snr_db)

    # Save signal
    signal_path = os.path.join(SIGNAL_DIR, f'{name.replace(" ","_")}.npy')
    np.save(signal_path, signal)
    md(f'- Signal saved to: `{os.path.basename(signal_path)}`')

    # Load signal (simulates file transfer)
    loaded = np.load(signal_path)

    # Decode
    t0    = time.time()
    stats = fsk.decode(loaded, len(bits))
    decode_time = time.time() - t0

    md(f'- Max amplitude: {stats["max_amplitude"]:.4f}')
    md(f'- Frame start: sample {stats["frame_start"]} ({stats["frame_start"]/fsk.sample_rate:.3f}s)')
    md(f'- Data start: sample {stats["data_start"]} ({stats["data_start"]/fsk.sample_rate:.3f}s)')
    md(f'- Expected frame start: ~{int(fsk.sample_rate * fsk.guard_duration)} samples ({fsk.guard_duration:.3f}s)')
    md(f'- Frame offset from expected: {stats["frame_start"] - int(fsk.sample_rate * fsk.guard_duration)} samples')
    md(f'- Decode time: {decode_time*1000:.1f}ms')
    md(f'- Decoded bits: `{stats["decoded_bits"][:32]}{"..." if len(stats["decoded_bits"])>32 else ""}`')

    if stats['errors']:
        for e in stats['errors']:
            md(f'-  Error: {e}')

    # Compare
    decoded = stats['decoded_bits']
    if len(decoded) == len(bits):
        errors = sum(1 for a, b in zip(bits, decoded) if a != b)
        ber    = errors / len(bits) * 100
        match  = errors == 0
        md(f'- Bit errors: {errors}/{len(bits)} (BER={ber:.1f}%)')
        md(f'- Result: {"PASS" if match else "FAIL"}')

        # Log first few symbol powers
        md('\n**Symbol power samples (first 8 bits):**')
        md('| Bit | P(f0=7kHz) | P(f1=9kHz) | Decoded |')
        md('|-----|-----------|-----------|---------|')
        for s in stats['symbol_powers'][:8]:
            md(f'| {s["bit"]} | {s["p0"]:.2f} | {s["p1"]:.2f} | `{s["decoded"]}` |')

        return match
    else:
        md(f'-  FAIL: decoded {len(decoded)} bits, expected {len(bits)}')
        return False


def run_test_with_presilence(fsk: FSKEngine, name: str, bits: str, presilence_s: float, snr_db: float = None) -> bool:
    """Test with N seconds of silence prepended — simulates iPhone recording before signal arrives"""
    md(f'\n### Test: {name}')
    md(f'- Input bits: `{bits[:32]}{"..." if len(bits)>32 else ""}`')
    md(f'- Bit count: {len(bits)}')
    md(f'- Pre-silence: {presilence_s:.1f}s (simulates recording starting before signal)')
    md(f'- SNR: {"clean (no noise)" if snr_db is None else f"{snr_db} dB"}')

    # Encode signal
    signal = fsk.encode(bits)

    # Prepend silence
    presilence = np.zeros(int(fsk.sample_rate * presilence_s), dtype=np.float32)
    signal     = np.concatenate([presilence, signal])

    if snr_db is not None:
        signal = fsk.add_noise(signal, snr_db)

    md(f'- Total signal length: {len(signal)} samples ({len(signal)/fsk.sample_rate:.3f}s)')
    md(f'- Signal arrives at: {presilence_s:.3f}s into recording')
    md(f'- Expected frame start: ~{int(fsk.sample_rate * (presilence_s + fsk.guard_duration))} samples ({presilence_s + fsk.guard_duration:.3f}s)')

    t0    = time.time()
    stats = fsk.decode(signal, len(bits))
    decode_time = time.time() - t0

    expected_frame = int(fsk.sample_rate * (presilence_s + fsk.guard_duration))
    md(f'- Frame start found: sample {stats["frame_start"]} ({stats["frame_start"]/fsk.sample_rate:.3f}s)')
    md(f'- Frame offset from expected: {stats["frame_start"] - expected_frame} samples')
    md(f'- Decode time: {decode_time*1000:.1f}ms')
    md(f'- Decoded bits: `{stats["decoded_bits"][:32]}{"..." if len(stats["decoded_bits"])>32 else ""}`')

    if stats['errors']:
        for e in stats['errors']:
            md(f'- Error: {e}')

    decoded = stats['decoded_bits']
    if len(decoded) == len(bits):
        errors = sum(1 for a, b in zip(bits, decoded) if a != b)
        ber    = errors / len(bits) * 100
        match  = errors == 0
        md(f'- Bit errors: {errors}/{len(bits)} (BER={ber:.1f}%)')
        md(f'- Result: {"PASS" if match else "FAIL"}')
        return match
    else:
        md(f'- FAIL: decoded {len(decoded)} bits, expected {len(bits)}')
        return False


def run_test_timing(fsk: FSKEngine, name: str, bits: str, presilence_s: float, snr_db: float = None) -> bool:
    """Test decode time specifically — simulates iPhone hardware performance"""
    md(f'\n### Timing Test: {name}')
    md(f'- Bit count: {len(bits)}, Pre-silence: {presilence_s:.1f}s, SNR: {"clean" if snr_db is None else f"{snr_db}dB"}')

    signal = fsk.encode(bits)
    presilence = np.zeros(int(fsk.sample_rate * presilence_s), dtype=np.float32)
    signal = np.concatenate([presilence, signal])
    if snr_db is not None:
        signal = fsk.add_noise(signal, snr_db)

    # Time each stage separately
    t0 = time.time()
    filtered = fsk.bandpass_filter(signal)
    t_filter = time.time() - t0

    t0 = time.time()
    frame_start = fsk.barker_sync(filtered)
    t_sync = time.time() - t0

    t0 = time.time()
    window, window_start = fsk.apply_agc_windowed(filtered, frame_start, len(bits))
    windowed_data_start = frame_start + 7 * fsk.samples_per_symbol - window_start
    decoded_bits = ''
    for i in range(len(bits)):
        sym_start = windowed_data_start + i * fsk.samples_per_symbol
        sym_end   = sym_start + fsk.samples_per_symbol
        if sym_end > len(window): break
        sym_data = window[sym_start:sym_end]
        p0 = fsk.goertzel(sym_data, fsk.f0)
        p1 = fsk.goertzel(sym_data, fsk.f1)
        decoded_bits += '1' if p1 > p0 else '0'
    t_demod = time.time() - t0

    total = t_filter + t_sync + t_demod
    errors = sum(1 for a, b in zip(bits, decoded_bits) if a != b) if len(decoded_bits) == len(bits) else -1

    md(f'| Stage | Time |')
    md(f'|-------|------|')
    md(f'| Bandpass filter | {t_filter*1000:.1f}ms |')
    md(f'| Barker sync | {t_sync*1000:.1f}ms |')
    md(f'| Goertzel demod | {t_demod*1000:.1f}ms |')
    md(f'| **Total** | **{total*1000:.1f}ms** |')
    md(f'- Frame start: sample {frame_start} ({frame_start/fsk.sample_rate:.3f}s)')
    md(f'- Bit errors: {errors}/{len(bits)}')
    md(f'- Result: {"PASS" if errors == 0 else "FAIL"}')
    return errors == 0


def run_all_tests():
    md('# FSK Signal Processing Test Report')
    md(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    md()
    md('## Configuration')
    fsk = FSKEngine()
    md(f'| Parameter | Value |')
    md(f'|-----------|-------|')
    md(f'| Sample rate | {fsk.sample_rate} Hz |')
    md(f'| f0 (bit 0) | {fsk.f0} Hz |')
    md(f'| f1 (bit 1) | {fsk.f1} Hz |')
    md(f'| Symbol duration | {fsk.symbol_duration*1000:.0f} ms |')
    md(f'| Guard interval | {fsk.guard_duration*1000:.0f} ms |')
    md(f'| Samples per symbol | {fsk.samples_per_symbol} |')
    md()

    crypto  = CryptographicCore(SHARED_KEY)
    results = {}

    #  Test 1: Sync pattern 
    md('## 1. Sync Pattern Tests')
    results['sync_clean'] = run_test(fsk, 'sync_clean', SYNC_PATTERN)
    results['sync_30dB']  = run_test(fsk, 'sync_30dB',  SYNC_PATTERN, snr_db=30)
    results['sync_20dB']  = run_test(fsk, 'sync_20dB',  SYNC_PATTERN, snr_db=20)
    results['sync_10dB']  = run_test(fsk, 'sync_10dB',  SYNC_PATTERN, snr_db=10)

    #  Test 2: Challenge (32 bits) 
    md('\n## 2. Challenge Tests (32 bits)')
    challenge = crypto.generate_challenge()
    challenge_bits = ''.join(format(b, '08b') for b in challenge)
    md(f'Challenge bytes: `{challenge.hex()}`')
    results['challenge_clean'] = run_test(fsk, 'challenge_clean', challenge_bits)
    results['challenge_30dB']  = run_test(fsk, 'challenge_30dB',  challenge_bits, snr_db=30)
    results['challenge_20dB']  = run_test(fsk, 'challenge_20dB',  challenge_bits, snr_db=20)
    results['challenge_10dB']  = run_test(fsk, 'challenge_10dB',  challenge_bits, snr_db=10)

    #  Test 3: Response (64 bits truncated HMAC) 
    md('\n## 3. Response Tests (64 bits)')
    response = crypto.compute_response(challenge)
    response_bits = ''.join(format(b, '08b') for b in response)
    md(f'Response bytes: `{response.hex()}`')
    results['response_clean'] = run_test(fsk, 'response_clean', response_bits)
    results['response_30dB']  = run_test(fsk, 'response_30dB',  response_bits, snr_db=30)
    results['response_20dB']  = run_test(fsk, 'response_20dB',  response_bits, snr_db=20)
    results['response_10dB']  = run_test(fsk, 'response_10dB',  response_bits, snr_db=10)

    #  Test 4: Full crypto round-trip 
    md('\n## 4. Full Crypto Round-Trip Test')
    md('Simulates complete laptopiPhonelaptop authentication:')

    challenge2      = crypto.generate_challenge()
    challenge2_bits = ''.join(format(b, '08b') for b in challenge2)
    response2       = crypto.compute_response(challenge2)
    response2_bits  = ''.join(format(b, '08b') for b in response2)

    md(f'- Challenge: `{challenge2.hex()}`')
    md(f'- Expected response: `{response2.hex()}`')

    # Encode challenge, decode it
    ch_signal  = fsk.encode(challenge2_bits)
    ch_stats   = fsk.decode(ch_signal, 32)
    ch_decoded = ch_stats['decoded_bits']

    if len(ch_decoded) == 32:
        ch_bytes = bytes(int(ch_decoded[i:i+8], 2) for i in range(0, 32, 8))
        md(f'- Decoded challenge: `{ch_bytes.hex()}`')
        md(f'- Challenge match: {"" if ch_bytes == challenge2 else ""}')

        # Compute response from decoded challenge
        resp_computed = crypto.compute_response(ch_bytes)
        resp_bits     = ''.join(format(b, '08b') for b in resp_computed)

        # Encode response, decode it
        resp_signal  = fsk.encode(resp_bits)
        resp_stats   = fsk.decode(resp_signal, 64)
        resp_decoded = resp_stats['decoded_bits']

        if len(resp_decoded) == 64:
            resp_bytes = bytes(int(resp_decoded[i:i+8], 2) for i in range(0, 64, 8))
            md(f'- Decoded response: `{resp_bytes.hex()}`')
            verified = crypto.verify_response(challenge2, resp_bytes)
            md(f'- HMAC verification: {" PASS" if verified else " FAIL"}')
            results['crypto_roundtrip'] = verified
        else:
            md(f'-  Response decode failed: got {len(resp_decoded)} bits')
            results['crypto_roundtrip'] = False
    else:
        md(f'-  Challenge decode failed: got {len(ch_decoded)} bits')
        results['crypto_roundtrip'] = False

    #  Test 5: Real audio simulation (pre-silence)
    md('\n## 5. Real Audio Simulation Tests')
    md('Simulates iPhone recording starting before signal arrives.')
    md('Pre-silence = time between iPhone starting to record and laptop starting to transmit.')

    challenge3      = crypto.generate_challenge()
    challenge3_bits = ''.join(format(b, '08b') for b in challenge3)
    response3       = crypto.compute_response(challenge3)
    response3_bits  = ''.join(format(b, '08b') for b in response3)

    md(f'\nChallenge bytes: `{challenge3.hex()}`')
    md(f'Response bytes: `{response3.hex()}`')

    # Sync with different pre-silence durations
    md('\n### 5a. Sync pattern with pre-silence')
    md('Exact timing: laptop waits TONE_DURATION(1.0s) + 0.3s + sentinel(0.3s) = 1.6s')
    results['sync_presilence_0.5s'] = run_test_with_presilence(fsk, 'sync_pre_0.5s', SYNC_PATTERN, 0.5)
    results['sync_presilence_1.0s'] = run_test_with_presilence(fsk, 'sync_pre_1.0s', SYNC_PATTERN, 1.0)
    results['sync_presilence_1.5s'] = run_test_with_presilence(fsk, 'sync_pre_1.5s', SYNC_PATTERN, 1.5)
    results['sync_presilence_2.0s'] = run_test_with_presilence(fsk, 'sync_pre_2.0s', SYNC_PATTERN, 2.0)
    results['sync_presilence_3.0s'] = run_test_with_presilence(fsk, 'sync_pre_3.0s', SYNC_PATTERN, 3.0)
    # Exact protocol timing: 1.6s +- 0.3s, extended to cover laptopAckWindow=3.0s
    results['sync_exact_1.3s']      = run_test_with_presilence(fsk, 'sync_exact_1.3s', SYNC_PATTERN, 1.3)
    results['sync_exact_1.6s']      = run_test_with_presilence(fsk, 'sync_exact_1.6s', SYNC_PATTERN, 1.6)
    results['sync_exact_1.9s']      = run_test_with_presilence(fsk, 'sync_exact_1.9s', SYNC_PATTERN, 1.9)
    results['sync_exact_2.5s']      = run_test_with_presilence(fsk, 'sync_exact_2.5s', SYNC_PATTERN, 2.5)
    results['sync_exact_3.0s']      = run_test_with_presilence(fsk, 'sync_exact_3.0s', SYNC_PATTERN, 3.0)
    # With noise
    results['sync_exact_1.3s_20dB'] = run_test_with_presilence(fsk, 'sync_exact_1.3s_20dB', SYNC_PATTERN, 1.3, snr_db=20)
    results['sync_exact_1.6s_20dB'] = run_test_with_presilence(fsk, 'sync_exact_1.6s_20dB', SYNC_PATTERN, 1.6, snr_db=20)
    results['sync_exact_1.9s_20dB'] = run_test_with_presilence(fsk, 'sync_exact_1.9s_20dB', SYNC_PATTERN, 1.9, snr_db=20)
    results['sync_exact_3.0s_20dB'] = run_test_with_presilence(fsk, 'sync_exact_3.0s_20dB', SYNC_PATTERN, 3.0, snr_db=20)

    # Challenge with pre-silence + noise
    md('\n### 5b. Challenge with pre-silence + noise')
    md('Exact timing: same as sync = 1.6s +- 0.3s')
    results['challenge_exact_1.3s']      = run_test_with_presilence(fsk, 'challenge_exact_1.3s',      challenge3_bits, 1.3)
    results['challenge_exact_1.6s']      = run_test_with_presilence(fsk, 'challenge_exact_1.6s',      challenge3_bits, 1.6)
    results['challenge_exact_1.9s']      = run_test_with_presilence(fsk, 'challenge_exact_1.9s',      challenge3_bits, 1.9)
    results['challenge_exact_3.0s']      = run_test_with_presilence(fsk, 'challenge_exact_3.0s',      challenge3_bits, 3.0)
    results['challenge_exact_1.3s_20dB'] = run_test_with_presilence(fsk, 'challenge_exact_1.3s_20dB', challenge3_bits, 1.3, snr_db=20)
    results['challenge_exact_1.6s_20dB'] = run_test_with_presilence(fsk, 'challenge_exact_1.6s_20dB', challenge3_bits, 1.6, snr_db=20)
    results['challenge_exact_1.9s_20dB'] = run_test_with_presilence(fsk, 'challenge_exact_1.9s_20dB', challenge3_bits, 1.9, snr_db=20)
    results['challenge_exact_3.0s_20dB'] = run_test_with_presilence(fsk, 'challenge_exact_3.0s_20dB', challenge3_bits, 3.0, snr_db=20)

    # Response with pre-silence + noise
    md('\n### 5c. Response with pre-silence + noise')
    md('Exact timing: laptop records immediately after challenge, response arrives ~0-1s later')
    results['response_exact_0.0s']      = run_test_with_presilence(fsk, 'response_exact_0.0s',      response3_bits, 0.0)
    results['response_exact_0.5s']      = run_test_with_presilence(fsk, 'response_exact_0.5s',      response3_bits, 0.5)
    results['response_exact_1.0s']      = run_test_with_presilence(fsk, 'response_exact_1.0s',      response3_bits, 1.0)
    results['response_exact_2.0s']      = run_test_with_presilence(fsk, 'response_exact_2.0s',      response3_bits, 2.0)
    results['response_exact_0.0s_20dB'] = run_test_with_presilence(fsk, 'response_exact_0.0s_20dB', response3_bits, 0.0, snr_db=20)
    results['response_exact_0.5s_20dB'] = run_test_with_presilence(fsk, 'response_exact_0.5s_20dB', response3_bits, 0.5, snr_db=20)
    results['response_exact_1.0s_20dB'] = run_test_with_presilence(fsk, 'response_exact_1.0s_20dB', response3_bits, 1.0, snr_db=20)
    results['response_exact_2.0s_20dB'] = run_test_with_presilence(fsk, 'response_exact_2.0s_20dB', response3_bits, 2.0, snr_db=20)

    #  Test 6: Decode timing breakdown
    md('\n## 6. Decode Timing Breakdown')
    md('Measures time for each decode stage to identify bottleneck.')
    md('iPhone ACK timeout is 5s — total decode must be under that.')

    results['timing_sync_1.6s']          = run_test_timing(fsk, 'sync_1.6s_presilence',      SYNC_PATTERN,    1.6)
    results['timing_challenge_1.6s']     = run_test_timing(fsk, 'challenge_1.6s_presilence',  challenge3_bits, 1.6)
    results['timing_response_0.5s']      = run_test_timing(fsk, 'response_0.5s_presilence',   response3_bits,  0.5)
    results['timing_sync_1.6s_20dB']     = run_test_timing(fsk, 'sync_1.6s_20dB',             SYNC_PATTERN,    1.6, snr_db=20)
    results['timing_challenge_1.6s_20dB']= run_test_timing(fsk, 'challenge_1.6s_20dB',        challenge3_bits, 1.6, snr_db=20)
    results['timing_response_0.5s_20dB'] = run_test_timing(fsk, 'response_0.5s_20dB',         response3_bits,  0.5, snr_db=20)

    #  Test 7: Barker sync position accuracy
    md('\n## 7. Barker Sync Position Accuracy')
    md('Verifies Barker sync finds the frame at the CORRECT position, not just decodes correctly.')
    md('A wrong position with lucky decoding would still pass Tests 1-6 but fail here.')
    md('Tolerance: ±1 symbol (~6615 samples) from expected frame start.')

    challenge4      = crypto.generate_challenge()
    challenge4_bits = ''.join(format(b, '08b') for b in challenge4)
    response4       = crypto.compute_response(challenge4)
    response4_bits  = ''.join(format(b, '08b') for b in response4)
    tolerance       = fsk.samples_per_symbol  # ±1 symbol

    def run_sync_position_test(name: str, bits: str, presilence_s: float, snr_db: float = None) -> bool:
        signal     = fsk.encode(bits)
        presilence = np.zeros(int(fsk.sample_rate * presilence_s), dtype=np.float32)
        signal     = np.concatenate([presilence, signal])
        if snr_db is not None:
            signal = fsk.add_noise(signal, snr_db)
        filtered   = fsk.bandpass_filter(signal)
        frame_start = fsk.barker_sync(filtered)
        expected    = int(fsk.sample_rate * (presilence_s + fsk.guard_duration))
        offset      = abs(frame_start - expected)
        passed      = offset <= tolerance
        md(f'- `{name}`: expected={expected} found={frame_start} offset={offset} samples ({'PASS' if passed else 'FAIL — sync missed signal'})')
        return passed

    md('\n**Challenge (32 bits) sync position:**')
    for ps, snr in [(0.5, None), (1.0, None), (1.6, None), (2.5, None), (3.0, None),
                    (1.6, 20),   (3.0, 20),   (1.6, 10),   (3.0, 10)]:
        label = f'challenge_{ps}s' + (f'_{snr}dB' if snr else '_clean')
        results[f'sync_pos_{label}'] = run_sync_position_test(label, challenge4_bits, ps, snr)

    md('\n**Response (64 bits) sync position:**')
    for ps, snr in [(0.0, None), (0.5, None), (1.0, None), (2.0, None),
                    (0.5, 20),   (2.0, 20),   (0.5, 10),   (2.0, 10)]:
        label = f'response_{ps}s' + (f'_{snr}dB' if snr else '_clean')
        results[f'sync_pos_{label}'] = run_sync_position_test(label, response4_bits, ps, snr)

    #  Summary 
    md('\n## Summary')
    md('| Test | Result |')
    md('|------|--------|')
    for name, passed in results.items():
        md(f'| {name} | {" PASS" if passed else " FAIL"} |')

    total  = len(results)
    passed = sum(results.values())
    md(f'\n**{passed}/{total} tests passed**')

    if passed == total:
        md('\n All signal processing tests passed  FSK pipeline is working correctly.')
    else:
        md(f'\n {total-passed} test(s) failed  check symbol powers table above for clues.')

    save_report()
    return passed == total


if __name__ == '__main__':
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    success = run_all_tests()
    sys.exit(0 if success else 1)
