"""
Tone generation and detection utilities for handshaking protocol
Provides simple single-frequency tone operations for READY/ACK/NACK signaling
"""

import numpy as np
import pyaudio

class ToneUtils:
    """
    Simple tone generation and detection for acoustic handshaking
    Uses single frequencies (not FSK) for control signals
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.audio = pyaudio.PyAudio()
        
    def generate_tone(self, frequency, duration, amplitude=0.3):
        """
        Generate a pure sine wave tone
        
        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
            
        Returns:
            numpy array of audio samples
        """
        samples = int(self.sample_rate * duration)
        t = np.arange(samples) / self.sample_rate
        tone = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in/out to reduce clicks
        fade_len = int(samples * 0.05)
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        tone[:fade_len] *= fade_in
        tone[-fade_len:] *= fade_out
        
        return tone.astype(np.float32)
    
    def play_tone(self, frequency, duration, amplitude=0.3):
        """
        Generate and play a tone through speakers
        
        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
        """
        tone = self.generate_tone(frequency, duration, amplitude)
        
        stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True
        )
        
        stream.write(tone.tobytes())
        stream.stop_stream()
        stream.close()
    
    def record_audio(self, duration):
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            numpy array of audio samples
        """
        stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=4096
        )
        
        frames = []
        samples_needed = int(self.sample_rate * duration)
        
        while len(frames) * 4096 < samples_needed:
            data = stream.read(4096, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.float32))
        
        stream.stop_stream()
        stream.close()
        
        audio = np.concatenate(frames)
        return audio[:samples_needed]
    
    def detect_tone(self, signal, frequency, threshold=50.0):
        """
        Detect presence of a specific frequency in signal using Goertzel algorithm
        
        Args:
            signal: Audio signal (numpy array)
            frequency: Target frequency in Hz
            threshold: Detection threshold (power level)
            
        Returns:
            True if tone detected, False otherwise
        """
        # Goertzel algorithm for single frequency detection
        N = len(signal)
        k = int(0.5 + (N * frequency / self.sample_rate))
        w = (2.0 * np.pi / N) * k
        cosine = np.cos(w)
        coeff = 2.0 * cosine
        
        q0, q1, q2 = 0.0, 0.0, 0.0
        
        for sample in signal:
            q0 = coeff * q1 - q2 + sample
            q2 = q1
            q1 = q0
        
        real = q1 - q2 * cosine
        imag = q2 * np.sin(w)
        power = np.sqrt(real * real + imag * imag)
        
        print(f"[ToneUtils] Frequency {int(frequency)}Hz: power={power:.2f}, threshold={threshold}")
        
        return power > threshold
    
    def detect_tone_chunked(self, frequency, max_duration=5.0, chunk_duration=0.5, threshold=50.0):
        """
        Detect tone in real-time chunks, returns as soon as tone is found
        Much faster than recording full duration then checking
        """
        chunks = int(max_duration / chunk_duration)
        for _ in range(chunks):
            signal = self.record_audio(chunk_duration)
            if self.detect_tone(signal, frequency, threshold=threshold):
                return True
        return False

    def cleanup(self):
        """Clean up PyAudio resources"""
        self.audio.terminate()
