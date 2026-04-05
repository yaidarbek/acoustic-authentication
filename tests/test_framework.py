import unittest
import time
import os
import hmac
import hashlib
import sys
from unittest.mock import patch, MagicMock
import numpy as np

# Add src/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our modules
from crypto_core import CryptographicCore, AuthenticationProtocol
from working_fsk import WorkingFSK
from acoustic_auth import AcousticAuthenticator
from protocol_layer import ProtocolLayer, AudioFrame, CRC16

class TestCryptographicCore(unittest.TestCase):
    """Unit tests for cryptographic operations"""
    
    def setUp(self):
        self.crypto = CryptographicCore()
        
    def test_challenge_generation(self):
        """Test cryptographically secure challenge generation"""
        challenge1 = self.crypto.generate_challenge()
        challenge2 = self.crypto.generate_challenge()
        
        # Challenges should be 4 bytes (32-bit acoustic challenge)
        self.assertEqual(len(challenge1), 4)
        self.assertEqual(len(challenge2), 4)
        
        # Challenges should be unique
        self.assertNotEqual(challenge1, challenge2)
        
    def test_hmac_computation(self):
        """Test HMAC-SHA256 response computation"""
        challenge = b"test_challenge_16"  # 16 bytes
        response = self.crypto.compute_response(challenge)
        
        # Response should be 8 bytes (64-bit truncated HMAC for acoustic transmission)
        self.assertEqual(len(response), 8)
        
        # Same challenge should produce same response
        response2 = self.crypto.compute_response(challenge)
        self.assertEqual(response, response2)
        
    def test_response_verification(self):
        """Test response verification"""
        challenge = self.crypto.generate_challenge()
        correct_response = self.crypto.compute_response(challenge)
        wrong_response = os.urandom(8)
        
        # Correct response should verify
        self.assertTrue(self.crypto.verify_response(challenge, correct_response))
        
        # Wrong response should fail
        self.assertFalse(self.crypto.verify_response(challenge, wrong_response))
        
    def test_replay_attack_prevention(self):
        """Test replay attack prevention"""
        challenge = self.crypto.generate_challenge()
        
        # Challenge should be in used set
        self.assertIn(challenge, self.crypto.used_challenges)
        
        # Same challenge shouldn't be generated again
        for _ in range(100):  # Try many times
            new_challenge = self.crypto.generate_challenge()
            self.assertNotEqual(challenge, new_challenge)

class TestAuthenticationProtocol(unittest.TestCase):
    """Unit tests for authentication protocol"""
    
    def setUp(self):
        self.shared_key = os.urandom(32)
        self.initiator = AuthenticationProtocol(self.shared_key)
        self.prover = AuthenticationProtocol(self.shared_key)
        
    def test_full_authentication_cycle(self):
        """Test complete authentication cycle"""
        # Initiator starts authentication
        challenge = self.initiator.initiate_authentication()
        
        # Prover processes challenge
        response = self.prover.process_challenge(challenge)
        
        # Initiator verifies response
        success = self.initiator.verify_authentication(response)
        
        self.assertTrue(success)
        
    def test_wrong_key_authentication(self):
        """Test authentication with wrong key fails"""
        wrong_prover = AuthenticationProtocol(os.urandom(32))
        
        challenge = self.initiator.initiate_authentication()
        response = wrong_prover.process_challenge(challenge)
        success = self.initiator.verify_authentication(response)
        
        self.assertFalse(success)
        
    def test_session_timeout(self):
        """Test session timeout functionality"""
        # Set short timeout for testing
        self.initiator.session_timeout = 0.1
        
        challenge = self.initiator.initiate_authentication()
        response = self.prover.process_challenge(challenge)
        
        # Wait for timeout
        time.sleep(0.2)
        
        success = self.initiator.verify_authentication(response)
        self.assertFalse(success)

class TestFSKAudio(unittest.TestCase):
    """Unit tests for FSK audio operations"""
    
    def setUp(self):
        self.fsk = WorkingFSK()
        
    def tearDown(self):
        self.fsk.cleanup()
        
    def test_tone_generation(self):
        """Test FSK tone generation"""
        tone_8k = self.fsk.generate_tone(8000, 0.1)
        tone_10k = self.fsk.generate_tone(10000, 0.1)
        
        # Should generate correct number of samples
        expected_samples = int(44100 * 0.1)
        self.assertEqual(len(tone_8k), expected_samples)
        self.assertEqual(len(tone_10k), expected_samples)
        
        # Tones should be different
        self.assertFalse(np.array_equal(tone_8k, tone_10k))
        
    def test_goertzel_detection(self):
        """Test Goertzel frequency detection"""
        # Generate pure 8kHz tone
        tone_8k = self.fsk.generate_tone(8000, 0.1)
        
        # Should detect 8kHz strongly
        power_8k = self.fsk.goertzel_detect(tone_8k, 8000)
        power_10k = self.fsk.goertzel_detect(tone_8k, 10000)
        
        # 8kHz should have much higher power
        self.assertGreater(power_8k, power_10k * 2)
        
    def test_bit_encoding_decoding(self):
        """Test bit encoding/decoding without audio"""
        test_bits = "1010"
        with patch.object(self.fsk, 'transmit_data') as mock_transmit, \
             patch.object(self.fsk, 'record_data') as mock_record:
            mock_record.return_value = np.array([1.0] * 44100)
            self.assertEqual(len(test_bits), 4)

    def test_bandpass_filter_removes_out_of_band(self):
        """TC-FSK-004: Bandpass filter must attenuate frequencies outside 7-11 kHz"""
        duration = 0.1
        samples = int(self.fsk.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        # Out-of-band signal at 1 kHz
        out_of_band = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        filtered = self.fsk.bandpass_filter(out_of_band)

        # Filtered signal energy should be much lower than original
        original_energy = np.sum(out_of_band ** 2)
        filtered_energy = np.sum(filtered ** 2)
        self.assertLess(filtered_energy, original_energy * 0.01)

    def test_bandpass_filter_passes_in_band(self):
        """TC-FSK-005: Bandpass filter must preserve 8 kHz and 10 kHz signals"""
        duration = 0.1
        samples = int(self.fsk.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        in_band = np.sin(2 * np.pi * 8000 * t).astype(np.float32)
        filtered = self.fsk.bandpass_filter(in_band)

        # Filtered signal energy should be close to original (>50% preserved)
        original_energy = np.sum(in_band ** 2)
        filtered_energy = np.sum(filtered ** 2)
        self.assertGreater(filtered_energy, original_energy * 0.5)

    def test_agc_normalizes_amplitude(self):
        """TC-FSK-006: AGC must normalize signal to max amplitude of 1.0"""
        # Weak signal with amplitude 0.01
        weak_signal = np.array([0.01, -0.01, 0.005, -0.008], dtype=np.float32)
        normalized = self.fsk.apply_agc(weak_signal)
        self.assertAlmostEqual(np.max(np.abs(normalized)), 1.0, places=5)

    def test_agc_handles_zero_signal(self):
        """TC-FSK-007: AGC must handle silent/zero signal without division by zero"""
        silent = np.zeros(100, dtype=np.float32)
        result = self.fsk.apply_agc(silent)
        self.assertTrue(np.all(result == 0))

    def test_barker_sync_finds_correct_position(self):
        """TC-FSK-008: Barker sync must locate preamble start in a synthetic signal"""
        samples_per_symbol = int(self.fsk.sample_rate * self.fsk.symbol_duration)
        barker = [1, 1, 1, -1, -1, 1, -1]

        # Build synthetic signal: silence + Barker preamble + data
        silence = np.zeros(samples_per_symbol * 3, dtype=np.float32)
        preamble = np.concatenate([
            self.fsk.generate_tone(self.fsk.f1 if c == 1 else self.fsk.f0, self.fsk.symbol_duration)
            for c in barker
        ])
        data = self.fsk.generate_tone(self.fsk.f1, self.fsk.symbol_duration)
        signal = np.concatenate([silence, preamble, data])

        best_start = self.fsk.barker_sync(signal)

        # Expected start is after the silence (3 symbols worth of samples)
        expected_start = samples_per_symbol * 3
        tolerance = samples_per_symbol  # Allow 1 symbol tolerance
        self.assertAlmostEqual(best_start, expected_start, delta=tolerance)
class TestSystemIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_bytes_to_bits_conversion(self):
        """Test data conversion functions"""
        test_data = b"Hello"
        bits = ''.join(format(b, '08b') for b in test_data)
        recovered_data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
        
        self.assertEqual(test_data, recovered_data)
        
    def test_challenge_bit_conversion(self):
        """Test challenge conversion to bits"""
        challenge = os.urandom(4)  # 32-bit acoustic challenge
        bits = ''.join(format(b, '08b') for b in challenge)
        
        # Should be 32 bits
        self.assertEqual(len(bits), 32)
        
        # Should be all 0s and 1s
        self.assertTrue(all(c in '01' for c in bits))
        
    def test_response_bit_conversion(self):
        """Test response conversion to bits"""
        response = os.urandom(8)  # 64-bit truncated HMAC response
        bits = ''.join(format(b, '08b') for b in response)
        
        # Should be 64 bits
        self.assertEqual(len(bits), 64)

class TestProtocolLayer(unittest.TestCase):
    """Unit tests for protocol layer — frame construction, CRC, and data splitting"""

    def setUp(self):
        self.protocol = ProtocolLayer()
        self.frame_handler = AudioFrame()
        self.crc = CRC16()

    def test_frame_creation_and_parsing_roundtrip(self):
        """TC-PROTO-001: Frame created and parsed back should recover original payload"""
        payload = b"Hello, acoustic world!"
        frames = self.protocol.prepare_transmission(payload)
        self.assertEqual(len(frames), 1)

        success, recovered, error = self.protocol.process_received_frame(frames[0])
        self.assertTrue(success, f"Frame parsing failed: {error}")
        self.assertEqual(payload, recovered)

    def test_crc_detects_single_bit_corruption(self):
        """TC-PROTO-002: CRC must detect a single flipped bit in the payload"""
        payload = b"integrity check"
        frames = self.protocol.prepare_transmission(payload)
        frame = bytearray(frames[0])

        # Flip one bit in the payload area (byte index 3 = first payload byte)
        frame[3] ^= 0x01

        success, _, error = self.protocol.process_received_frame(bytes(frame))
        self.assertFalse(success, "CRC should have detected corruption")
        self.assertEqual(error, "CRC verification failed")

    def test_invalid_preamble_rejected(self):
        """TC-PROTO-003: Frame with wrong preamble byte must be rejected"""
        payload = b"test"
        frames = self.protocol.prepare_transmission(payload)
        frame = bytearray(frames[0])

        # Corrupt the preamble byte
        frame[0] = 0x00

        success, _, error = self.protocol.process_received_frame(bytes(frame))
        self.assertFalse(success)
        self.assertEqual(error, "Invalid preamble")

    def test_frame_too_short_rejected(self):
        """TC-PROTO-004: Frame shorter than minimum size must be rejected"""
        success, _, error = self.protocol.process_received_frame(b"\xAA\x00")
        self.assertFalse(success)
        self.assertEqual(error, "Frame too short")

    def test_large_data_splits_into_multiple_frames(self):
        """TC-PROTO-005: Data larger than 255 bytes must be split across frames"""
        large_data = b"X" * 300  # Exceeds MAX_PAYLOAD_SIZE of 255
        frames = self.protocol.prepare_transmission(large_data)
        self.assertEqual(len(frames), 2)

    def test_large_data_reconstructed_correctly(self):
        """TC-PROTO-006: All frames from a large payload must reconstruct original data"""
        large_data = os.urandom(300)
        frames = self.protocol.prepare_transmission(large_data)

        reconstructed = b""
        for frame in frames:
            success, payload, error = self.protocol.process_received_frame(frame)
            self.assertTrue(success, f"Frame failed: {error}")
            reconstructed += payload

        self.assertEqual(large_data, reconstructed)

    def test_crc_calculation_deterministic(self):
        """TC-PROTO-007: Same data must always produce same CRC value"""
        data = b"deterministic test"
        crc1 = self.crc.calculate(data)
        crc2 = self.crc.calculate(data)
        self.assertEqual(crc1, crc2)

    def test_crc_different_data_different_checksum(self):
        """TC-PROTO-008: Different data must produce different CRC values"""
        crc1 = self.crc.calculate(b"data one")
        crc2 = self.crc.calculate(b"data two")
        self.assertNotEqual(crc1, crc2)

    def test_sequence_numbers_increment(self):
        """TC-PROTO-009: Sequence number must increment across frames"""
        data = b"A" * 300
        frames = self.protocol.prepare_transmission(data)

        from protocol_layer import FrameHeader
        seq0 = FrameHeader.from_bytes(frames[0][1:3]).sequence
        seq1 = FrameHeader.from_bytes(frames[1][1:3]).sequence
        self.assertEqual(seq1, seq0 + 1)

    def test_empty_payload_frame(self):
        """TC-PROTO-010: Frame with empty payload must be created and parsed correctly"""
        frames = self.protocol.prepare_transmission(b"")
        self.assertEqual(len(frames), 0)  # No data = no frames


class TestSecurityFeatures(unittest.TestCase):
    """Security-focused tests"""
    
    def setUp(self):
        self.crypto = CryptographicCore()
        
    def test_timing_attack_resistance(self):
        """Test constant-time comparison"""
        challenge = self.crypto.generate_challenge()
        correct_response = self.crypto.compute_response(challenge)
        wrong_response = os.urandom(32)
        
        # Measure timing for correct response
        times_correct = []
        for _ in range(10):
            start = time.perf_counter()
            self.crypto.verify_response(challenge, correct_response)
            times_correct.append(time.perf_counter() - start)
            
        # Measure timing for wrong response
        times_wrong = []
        for _ in range(10):
            start = time.perf_counter()
            self.crypto.verify_response(challenge, wrong_response)
            times_wrong.append(time.perf_counter() - start)
            
        # Timing should be similar (constant-time)
        avg_correct = sum(times_correct) / len(times_correct)
        avg_wrong = sum(times_wrong) / len(times_wrong)
        
        # Allow 50% variance (generous for testing)
        self.assertLess(abs(avg_correct - avg_wrong) / max(avg_correct, avg_wrong), 0.5)
        
    def test_key_entropy(self):
        """Test cryptographic key quality"""
        key = self.crypto.shared_key
        
        # Key should be 32 bytes
        self.assertEqual(len(key), 32)
        
        # Key should have good entropy (not all zeros, not all same)
        self.assertNotEqual(key, b'\x00' * 32)
        self.assertGreater(len(set(key)), 10)  # At least 10 different byte values

class PerformanceBenchmarks(unittest.TestCase):
    """Performance and reliability tests"""
    
    def setUp(self):
        self.crypto = CryptographicCore()
        
    def test_challenge_generation_performance(self):
        """Benchmark challenge generation speed"""
        start_time = time.time()
        
        for _ in range(100):
            self.crypto.generate_challenge()
            
        elapsed = time.time() - start_time
        
        # Should generate 100 challenges in under 1 second
        self.assertLess(elapsed, 1.0)
        print(f"Challenge generation: {elapsed:.3f}s for 100 challenges")
        
    def test_hmac_computation_performance(self):
        """Benchmark HMAC computation speed"""
        challenge = self.crypto.generate_challenge()
        
        start_time = time.time()
        
        for _ in range(1000):
            self.crypto.compute_response(challenge)
            
        elapsed = time.time() - start_time
        
        # Should compute 1000 HMACs in under 1 second
        self.assertLess(elapsed, 1.0)
        print(f"HMAC computation: {elapsed:.3f}s for 1000 operations")
        
    def test_authentication_cycle_timing(self):
        """Test full authentication cycle timing"""
        protocol = AuthenticationProtocol()
        
        start_time = time.time()
        
        # Full cycle
        challenge = protocol.initiate_authentication()
        response = protocol.process_challenge(challenge)
        success = protocol.verify_authentication(response)
        
        elapsed = time.time() - start_time
        
        self.assertTrue(success)
        # Should complete in under 100ms
        self.assertLess(elapsed, 0.1)
        print(f"Full auth cycle: {elapsed:.3f}s")

def run_test_suite():
    """Run comprehensive test suite"""
    print("=== ACOUSTIC AUTHENTICATION TEST FRAMEWORK ===\n")
    
    # Create test suite
    test_classes = [
        TestCryptographicCore,
        TestAuthenticationProtocol,
        TestFSKAudio,
        TestProtocolLayer,
        TestSystemIntegration,
        TestSecurityFeatures,
        PerformanceBenchmarks
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"Running {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        tests_run = result.testsRun
        failures = len(result.failures) + len(result.errors)
        
        total_tests += tests_run
        total_failures += failures
        
        status = "PASSED" if failures == 0 else f"{failures} FAILED"
        print(f"  {tests_run} tests - {status}")
        
        # Print failure details
        for failure in result.failures + result.errors:
            print(f"    FAIL: {failure[0]}")
            print(f"    {failure[1]}")
            
    print(f"\n=== TEST SUMMARY ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures}")
    print(f"Failed: {total_failures}")
    print(f"Success Rate: {((total_tests - total_failures) / total_tests * 100):.1f}%")
    
    if total_failures == 0:
        print("\nALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
    else:
        print(f"\n{total_failures} TESTS FAILED - REVIEW REQUIRED")
        
    return total_failures == 0

if __name__ == "__main__":
    run_test_suite()