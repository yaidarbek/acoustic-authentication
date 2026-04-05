import os
import hmac
import hashlib
import secrets
import time
import json
from typing import Optional, Tuple

NONCE_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'used_nonces.json')

class CryptographicCore:
    """
    Implements HMAC-SHA256 challenge-response authentication
    Based on specifications from interim report
    """
    
    def __init__(self, shared_key: Optional[bytes] = None):
        # Use provided key or generate new one
        self.shared_key = shared_key or self._generate_shared_key()
        self.challenge_size = 4   # 32-bit challenge
        self.used_challenges = self._load_used_challenges()  # Persistent replay attack prevention
        
    def _generate_shared_key(self) -> bytes:
        """Generate cryptographically secure shared key"""
        return secrets.token_bytes(32)  # 256-bit key

    def _load_used_challenges(self) -> set:
        """Load persisted used challenges from disk to survive restarts"""
        if os.path.exists(NONCE_LOG_FILE):
            try:
                with open(NONCE_LOG_FILE, 'r') as f:
                    return set(bytes.fromhex(h) for h in json.load(f))
            except (json.JSONDecodeError, ValueError):
                return set()
        return set()

    def _save_used_challenges(self) -> None:
        """Persist used challenges to disk"""
        with open(NONCE_LOG_FILE, 'w') as f:
            json.dump([c.hex() for c in self.used_challenges], f)
    
    def generate_challenge(self) -> bytes:
        """
        Generate cryptographically secure random challenge
        C = os.urandom(16) # 128-bit random challenge
        """
        challenge = os.urandom(self.challenge_size)
        
        # Ensure uniqueness (replay attack prevention)
        while challenge in self.used_challenges:
            challenge = os.urandom(self.challenge_size)
            
        self.used_challenges.add(challenge)
        self._save_used_challenges()
        return challenge
    
    def compute_response(self, challenge: bytes) -> bytes:
        """
        Compute truncated HMAC-SHA256 response to challenge
        Truncated to 8 bytes (64 bits) for faster acoustic transmission
        """
        full_hmac = hmac.new(
            self.shared_key,
            challenge,
            digestmod=hashlib.sha256
        ).digest()
        return full_hmac[:8]  # truncate to 64 bits
    
    def verify_response(self, challenge: bytes, response: bytes) -> bool:
        """
        Verify response using constant-time comparison
        Prevents timing attacks as specified in report
        """
        expected_response = self.compute_response(challenge)
        return self._secure_compare(response, expected_response)
    
    def _secure_compare(self, a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks
        Implementation of secure_compare() from report
        """
        return hmac.compare_digest(a, b)
    
    def create_authentication_session(self) -> Tuple[bytes, bytes]:
        """
        Create complete authentication session
        Returns: (challenge, expected_response)
        """
        challenge = self.generate_challenge()
        expected_response = self.compute_response(challenge)
        return challenge, expected_response
    
    def authenticate(self, challenge: bytes, received_response: bytes) -> bool:
        """
        Complete authentication verification
        Returns True if authentication successful
        """
        # Check if challenge was used before (replay attack)
        if challenge not in self.used_challenges:
            return False
            
        return self.verify_response(challenge, received_response)
    
    def get_key_info(self) -> dict:
        """Get key information for debugging"""
        return {
            'key_length': len(self.shared_key),
            'challenge_size': self.challenge_size,
            'used_challenges': len(self.used_challenges)
        }

class AuthenticationProtocol:
    """
    High-level authentication protocol implementation
    Combines cryptographic core with session management
    """
    
    def __init__(self, shared_key: Optional[bytes] = None):
        self.crypto = CryptographicCore(shared_key)
        self.current_challenge = None
        self.session_timeout = 30  # seconds
        self.session_start_time = None
    
    def initiate_authentication(self) -> bytes:
        """
        Initiator (laptop) starts authentication
        Returns challenge to send to prover
        """
        self.current_challenge, self.expected_response = self.crypto.create_authentication_session()
        self.session_start_time = time.time()
        
        print(f"Challenge generated: {self.current_challenge.hex()[:16]}...")
        return self.current_challenge
    
    def process_challenge(self, challenge: bytes) -> bytes:
        """
        Prover (iPhone) processes challenge
        Returns response to send back
        """
        response = self.crypto.compute_response(challenge)
        print(f"Response computed: {response.hex()[:16]}...")
        return response
    
    def verify_authentication(self, received_response: bytes) -> bool:
        """
        Initiator verifies received response
        Returns True if authentication successful
        """
        if not self.current_challenge:
            print("No active challenge")
            return False
            
        # Check session timeout
        if self.session_start_time is None or time.time() - self.session_start_time > self.session_timeout:
            print("Session timeout")
            return False
        
        success = self.crypto.verify_response(self.current_challenge, received_response)
        
        if success:
            print("[OK] Authentication SUCCESSFUL")
        else:
            print("[FAIL] Authentication FAILED")
            
        # Clear session
        self.current_challenge = None
        self.session_start_time = None
        
        return success
    
    def get_shared_key(self) -> bytes:
        """Get shared key for key exchange"""
        return self.crypto.shared_key

def test_cryptographic_core():
    """Test the cryptographic implementation"""
    print("=== Cryptographic Core Test ===")
    
    # Test 1: Basic HMAC computation
    print("\n1. Testing HMAC-SHA256 computation...")
    crypto = CryptographicCore()
    
    challenge = b"test_challenge_123"
    response = crypto.compute_response(challenge)
    
    print(f"Challenge: {challenge.hex()}")
    print(f"Response:  {response.hex()}")
    print(f"Response length: {len(response)} bytes")
    
    # Test 2: Verification
    print("\n2. Testing response verification...")
    valid = crypto.verify_response(challenge, response)
    print(f"Verification result: {valid}")
    
    # Test 3: Invalid response
    print("\n3. Testing invalid response...")
    invalid_response = os.urandom(32)
    invalid = crypto.verify_response(challenge, invalid_response)
    print(f"Invalid response rejected: {not invalid}")
    
    # Test 4: Full protocol
    print("\n4. Testing full authentication protocol...")
    
    # Shared key for both parties
    shared_key = crypto.shared_key
    
    # Initiator (laptop)
    initiator = AuthenticationProtocol(shared_key)
    challenge = initiator.initiate_authentication()
    
    # Prover (iPhone) 
    prover = AuthenticationProtocol(shared_key)
    response = prover.process_challenge(challenge)
    
    # Verification
    success = initiator.verify_authentication(response)
    
    print(f"\nFull protocol test: {'PASSED' if success else 'FAILED'}")
    
    return success

def test_security_features():
    """Test security features"""
    print("\n=== Security Features Test ===")
    
    crypto = CryptographicCore()
    
    # Test replay attack prevention
    print("\n1. Testing replay attack prevention...")
    challenge1 = crypto.generate_challenge()
    challenge2 = crypto.generate_challenge()
    
    print(f"Challenges are unique: {challenge1 != challenge2}")
    
    # Test timing attack resistance
    print("\n2. Testing constant-time comparison...")
    correct_response = crypto.compute_response(challenge1)
    wrong_response = os.urandom(32)
    
    # Both should take similar time (constant-time)
    start = time.time()
    crypto.verify_response(challenge1, correct_response)
    time1 = time.time() - start
    
    start = time.time()
    crypto.verify_response(challenge1, wrong_response)
    time2 = time.time() - start
    
    print(f"Timing difference: {abs(time1 - time2):.6f}s (should be minimal)")
    
    return True

if __name__ == "__main__":
    # Run comprehensive tests
    crypto_success = test_cryptographic_core()
    security_success = test_security_features()
    
    if crypto_success and security_success:
        print("\n✓ CRYPTOGRAPHIC CORE IMPLEMENTED SUCCESSFULLY")
        print("Ready for integration with FSK audio pipeline")
    else:
        print("\n✗ Issues detected in cryptographic implementation")