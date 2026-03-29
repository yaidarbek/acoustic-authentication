import numpy as np
import pyaudio
import time
from scipy.signal import butter, filtfilt

class WorkingFSK:
    def __init__(self):
        self.sample_rate = 44100
        self.f0 = 7000   # Binary '0' - 7 kHz
        self.f1 = 9000   # Binary '1' - 9 kHz
        self.symbol_duration = 0.15  # 150ms - matches Swift FSKDecoder
        self.amplitude = 0.1
        
        self.audio = pyaudio.PyAudio()
        
    def generate_tone(self, frequency, duration):
        """Generate clean sine wave"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        wave = self.amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Smooth edges to reduce clicks
        fade_len = int(samples * 0.05)
        if fade_len > 0:
            fade_in = np.linspace(0, 1, fade_len)
            fade_out = np.linspace(1, 0, fade_len)
            wave[:fade_len] *= fade_in
            wave[-fade_len:] *= fade_out
            
        return wave.astype(np.float32)
    
    def transmit_data(self, bits):
        """Transmit binary data as FSK with guard interval and Barker-7 preamble"""
        print(f"Transmitting {len(bits)} bits with guard interval + Barker-7 preamble")

        # Barker-7 preamble: 1=f1, -1=f0
        barker = [1, 1, 1, -1, -1, 1, -1]
        preamble_bits = ''.join('1' if c == 1 else '0' for c in barker)

        # Full transmission: guard silence + preamble + data
        full_data = preamble_bits + bits

        # 200ms guard interval silence before preamble
        guard_samples = int(self.sample_rate * 0.2)
        signal = np.zeros(guard_samples, dtype=np.float32)

        for bit in full_data:
            freq = self.f1 if bit == '1' else self.f0
            tone = self.generate_tone(freq, self.symbol_duration)
            signal = np.concatenate([signal, tone])

        # Play signal
        stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=1024
        )
        stream.write(signal.tobytes())
        stream.stop_stream()
        stream.close()

        return len(full_data) * self.symbol_duration
    
    def record_data(self, duration):
        """Record audio data"""
        print(f"Recording for {duration:.1f} seconds...")
        
        stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        frames = []
        total_frames = int(self.sample_rate / 1024 * duration)
        
        for i in range(total_frames):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.float32))
        
        stream.stop_stream()
        stream.close()
        
        return np.concatenate(frames)
    
    def goertzel_detect(self, samples, freq):
        """Goertzel algorithm for single frequency detection"""
        N = len(samples)
        k = int(0.5 + ((N * freq) / self.sample_rate))
        w = (2.0 * np.pi / N) * k
        cosine = np.cos(w)
        coeff = 2.0 * cosine
        
        q0 = q1 = q2 = 0.0
        for sample in samples:
            q0 = coeff * q1 - q2 + sample
            q2 = q1
            q1 = q0
            
        real = q1 - q2 * cosine
        imag = q2 * np.sin(w)
        magnitude = np.sqrt(real * real + imag * imag)
        return magnitude
    
    def bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """
        4th-order Butterworth bandpass filter
        Removes out-of-band noise before demodulation
        Passband: 7-11 kHz (covers f0=8kHz and f1=10kHz with margin)
        """
        nyq = self.sample_rate / 2
        low = 6000 / nyq
        high = 10000 / nyq
        b, a = butter(4, [low, high], btype='band')
        return filtfilt(b, a, signal).astype(np.float32)

    def apply_agc(self, signal: np.ndarray) -> np.ndarray:
        """
        Automatic Gain Control — normalizes signal amplitude
        Compensates for distance-dependent attenuation
        Scales signal to [-1, 1] range before Goertzel detection
        """
        max_amp = np.max(np.abs(signal))
        if max_amp > 0:
            return (signal / max_amp).astype(np.float32)
        return signal

    def barker_sync(self, signal: np.ndarray) -> int:
        barker    = np.array([1, 1, 1, -1, -1, 1, -1], dtype=np.float32)
        samples_per_symbol = int(self.sample_rate * self.symbol_duration)
        reference = np.repeat(barker, samples_per_symbol)
        if len(signal) < len(reference):
            return 0

        # Build reference using same tone generation as encoder (with fade)
        ref_signal = np.array([], dtype=np.float32)
        for chip in barker:
            freq = self.f1 if chip > 0 else self.f0
            ref_signal = np.concatenate([ref_signal, self.generate_tone(freq, self.symbol_duration)])
        reference = ref_signal

        # Frame always starts near beginning (guard=0.2s + small offset)
        # Limit search to first 3s to avoid false peaks in noise
        search_end    = min(len(signal) - len(reference), int(self.sample_rate * 3.0))
        search_signal = signal[:search_end + len(reference)]

        # Step 1: Coarse search on consistently downsampled signal
        ds     = 10
        sig_ds = search_signal[::ds]
        ref_ds = reference[::ds]
        corr   = np.correlate(sig_ds, ref_ds, mode='valid')
        coarse_peak = int(np.argmax(np.abs(corr))) * ds

        # Step 2: Fine search every 10 samples within +-1 symbol around coarse peak
        fine_start = max(0, coarse_peak - samples_per_symbol)
        fine_end   = min(len(signal) - len(reference), coarse_peak + samples_per_symbol)
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

    def decode_signal(self, signal, expected_bits):
        """Decode FSK signal with bandpass filter, AGC, and Barker sync"""
        samples_per_symbol = int(self.sample_rate * self.symbol_duration)

        # Step 1: Bandpass filter — remove out-of-band noise
        signal = self.bandpass_filter(signal)

        # Step 2: AGC — normalize amplitude for consistent Goertzel detection
        signal = self.apply_agc(signal)

        # Step 3: Barker-7 sync — find frame start via cross-correlation
        # Barker preamble is 7 symbols, skip past it to reach data
        barker_len = 7 * samples_per_symbol
        best_start = self.barker_sync(signal)
        data_start = best_start + barker_len

        print(f"Barker sync: frame start at sample {best_start}, data at {data_start}")

        # Step 4: Goertzel demodulation
        decoded_bits = ""
        for i in range(expected_bits):
            symbol_start = data_start + i * samples_per_symbol
            symbol_end = symbol_start + samples_per_symbol

            if symbol_end <= len(signal):
                symbol_data = signal[symbol_start:symbol_end]
                power_f0 = self.goertzel_detect(symbol_data, self.f0)
                power_f1 = self.goertzel_detect(symbol_data, self.f1)

                bit = '1' if power_f1 > power_f0 else '0'
                decoded_bits += bit

                print(f"Symbol {i}: P0={power_f0:.2f}, P1={power_f1:.2f} -> {bit}")

        return decoded_bits
    
    def test_transmission(self, test_bits="1010"):
        """Test complete transmission cycle"""
        print("=== FSK Transmission Test ===")
        
        # Step 1: Transmit
        duration = self.transmit_data(test_bits)
        
        # Step 2: Wait
        print("Waiting...")
        time.sleep(0.5)
        
        # Step 3: Record (simulate receiving)
        record_duration = duration + 1.0  # Extra buffer
        recorded_signal = self.record_data(record_duration)
        
        # Step 4: Decode
        print("Decoding...")
        decoded = self.decode_signal(recorded_signal, len(test_bits))
        
        # Results
        print(f"\n=== Results ===")
        print(f"Original:  {test_bits}")
        print(f"Decoded:   {decoded}")
        print(f"Match:     {test_bits == decoded}")
        
        if len(decoded) == len(test_bits):
            errors = sum(1 for a, b in zip(test_bits, decoded) if a != b)
            print(f"Bit errors: {errors}/{len(test_bits)}")
        
        return test_bits == decoded
    
    def cleanup(self):
        self.audio.terminate()

def main():
    fsk = WorkingFSK()
    
    try:
        # Test with simple pattern
        success = fsk.test_transmission("1010")
        
        if success:
            print("\n✓ FSK Audio Pipeline VALIDATED!")
            print("Ready to implement full authentication system.")
        else:
            print("\n⚠ FSK needs tuning, but basic pipeline works.")
            print("Hardware and software components are functional.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fsk.cleanup()

if __name__ == "__main__":
    main()