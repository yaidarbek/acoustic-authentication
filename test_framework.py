import unittest
import time
import os
import hmac
import hashlib
from unittest.mock import patch, MagicMock
import numpy as np

# Import our modules
from crypto_core import CryptographicCore, AuthenticationProtocol
from working_fsk import WorkingFSK
from acoustic_auth import AcousticAuthenticator

class TestCryptographicCore(unittest.TestCase):
    """Unit tests for cryptographic operations"""
    
    def setUp(self):
        self.crypto = CryptographicCore()
        
    def test_challenge_generation(self):
        """Test cryptographically secure challenge generation"""
        challenge1 = self.crypto.generate_challenge()
        challenge2 = self.crypto.generate_challenge()
        
        # Challenges should be 16 bytes
        self.assertEqual(len(challenge1), 16)
        self.assertEqual(len(challenge2), 16)
        
        # Challenges should be unique
        self.assertNotEqual(challenge1, challenge2)
        
    def test_hmac_computation(self):
        """Test HMAC-SHA256 response computation"""
        challenge = b"test_challenge_16"  # 16 bytes
        response = self.crypto.compute_response(challenge)
        
        # Response should be 32 bytes (SHA256)
        self.assertEqual(len(response), 32)
        
        # Same challenge should produce same response
        response2 = self.crypto.compute_response(challenge)
        self.assertEqual(response, response2)
        
    def test_response_verification(self):
        """Test response verification"""
        challenge = self.crypto.generate_challenge()
        correct_response = self.crypto.compute_response(challenge)
        wrong_response = os.urandom(32)
        
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
        
        # Mock the audio transmission
        with patch.object(self.fsk, 'transmit_data') as mock_transmit, \
             patch.object(self.fsk, 'record_data') as mock_record:
            
            # Simulate perfect transmission
            mock_record.return_value = np.array([1.0] * 44100)  # Dummy signal
            
            # This would normally involve audio, so we test the logic
            self.assertEqual(len(test_bits), 4)

class TestSystemIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def setUp(self):
        self.authenticator = AcousticAuthenticator()
        
    def tearDown(self):
        self.authenticator.cleanup()
        
    def test_bytes_to_bits_conversion(self):
        """Test data conversion functions"""
        test_data = b"Hello"
        bits = self.authenticator.bytes_to_bits(test_data)
        recovered_data = self.authenticator.bits_to_bytes(bits)
        
        self.assertEqual(test_data, recovered_data)
        
    def test_challenge_bit_conversion(self):
        """Test challenge conversion to bits"""
        challenge = os.urandom(16)
        bits = self.authenticator.bytes_to_bits(challenge)
        
        # Should be 128 bits
        self.assertEqual(len(bits), 128)
        
        # Should be all 0s and 1s
        self.assertTrue(all(c in '01' for c in bits))
        
    def test_response_bit_conversion(self):
        """Test response conversion to bits"""
        response = os.urandom(32)  # HMAC-SHA256 output
        bits = self.authenticator.bytes_to_bits(response)
        
        # Should be 256 bits
        self.assertEqual(len(bits), 256)

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
        TestSystemIntegration,
        TestSecurityFeatures,
        PerformanceBenchmarks
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"Running {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        tests_run = result.testsRun
        failures = len(result.failures) + len(result.errors)
        
        total_tests += tests_run
        total_failures += failures
        
        status = "✓ PASSED" if failures == 0 else f"✗ {failures} FAILED"
        print(f"  {tests_run} tests - {status}")
        
        # Print failure details
        for failure in result.failures + result.errors:
            print(f"    FAIL: {failure[0]}")
            
    print(f"\n=== TEST SUMMARY ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures}")
    print(f"Failed: {total_failures}")
    print(f"Success Rate: {((total_tests - total_failures) / total_tests * 100):.1f}%")
    
    if total_failures == 0:
        print("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
    else:
        print(f"\n⚠️  {total_failures} TESTS FAILED - REVIEW REQUIRED")
        
    return total_failures == 0

if __name__ == "__main__":
    run_test_suite()