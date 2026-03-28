import time
from crypto_core import AuthenticationProtocol
from enhanced_fsk import EnhancedFSK
from tone_utils import ToneUtils

class AcousticAuthenticator:
    """
    Integrated acoustic authentication system with handshaking protocol
    Combines FSK audio transmission with HMAC-SHA256 cryptography
    Full stack: FSK -> Protocol Layer (framing + CRC-16) -> HMAC-SHA256
    
    Protocol flow:
    1. Laptop sends READY tone (12 kHz)
    2. iPhone responds with ACK tone (14 kHz)
    3. Laptop sends challenge (FSK)
    4. iPhone sends response (FSK)
    5. Laptop sends ACK (12 kHz) or NACK (6 kHz)
    """

    def __init__(self, shared_key=None):
        self.auth_protocol = AuthenticationProtocol(shared_key)
        self.fsk = EnhancedFSK()
        self.tone_utils = ToneUtils()
        # Extend session timeout for testing
        self.auth_protocol.session_timeout = 60  # 60 seconds for testing
        
        # Handshaking tone frequencies
        self.READY_FREQ = 12000.0  # 12 kHz - READY from laptop
        self.ACK_FREQ = 14000.0    # 14 kHz - ACK from iPhone
        self.NACK_FREQ = 6000.0    # 6 kHz - NACK from laptop
        self.TONE_DURATION = 0.5   # 0.5 seconds
        self.SUCCESS_TONE_DURATION = 1.0  # 1 second for final ACK/NACK

    def bytes_to_bits(self, data: bytes) -> str:
        """Convert bytes to binary string"""
        return ''.join(format(byte, '08b') for byte in data)

    def bits_to_bytes(self, bits: str) -> bytes:
        """Convert binary string to bytes"""
        while len(bits) % 8 != 0:
            bits += '0'
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    
    # ========== Handshaking Functions ==========
    
    def send_ready_tone(self):
        """Laptop: Send READY tone to signal readiness"""
        print("📡 Sending READY tone (12 kHz)...")
        self.tone_utils.play_tone(self.READY_FREQ, self.TONE_DURATION)
        print("✅ READY tone sent")
    
    def listen_for_ack(self, timeout=10.0):
        """Laptop: Listen for ACK tone from iPhone"""
        print(f"👂 Listening for ACK tone ({timeout}s timeout)...")
        signal = self.tone_utils.record_audio(timeout)
        detected = self.tone_utils.detect_tone(signal, self.ACK_FREQ, threshold=50.0)
        
        if detected:
            print("✅ ACK tone detected - iPhone connected")
            return True
        else:
            print("❌ ACK tone not detected")
            return False
    
    def send_ack_tone(self):
        """Laptop: Send ACK tone (success)"""
        print("📡 Sending ACK tone (authentication successful)...")
        self.tone_utils.play_tone(self.READY_FREQ, self.SUCCESS_TONE_DURATION)
        print("✅ ACK sent")
    
    def send_nack_tone(self):
        """Laptop: Send NACK tone (failure)"""
        print("📡 Sending NACK tone (authentication failed)...")
        self.tone_utils.play_tone(self.NACK_FREQ, self.SUCCESS_TONE_DURATION)
        print("✅ NACK sent")
    
    # ========== Authentication Functions ==========
    
    def transmit_challenge(self) -> bytes:
        """
        Laptop: Generate and transmit challenge acoustically via protocol layer
        Returns the challenge for verification
        """
        print("=== INITIATING ACOUSTIC AUTHENTICATION ===")

        challenge = self.auth_protocol.initiate_authentication()
        print(f"Challenge: {challenge.hex()}")

        # Transmit via EnhancedFSK — applies framing + CRC-16 automatically
        print("Transmitting challenge acoustically (with protocol layer)...")
        self.fsk.transmit_data_with_protocol(challenge)

        return challenge

    def receive_challenge(self, duration=None) -> bytes:
        """
        iPhone: Record and decode challenge via protocol layer
        Returns decoded challenge
        """
        print("=== RECEIVING ACOUSTIC CHALLENGE ===")

        # Challenge is 16 bytes + protocol overhead (5 bytes) = 21 bytes = 168 bits
        if duration is None:
            frame_bits = (16 + 5) * 8  # payload + protocol overhead
            duration = frame_bits * self.fsk.symbol_duration + 1.0

        print(f"Recording for {duration:.1f} seconds...")
        rx_stats = self.fsk.receive_data_with_protocol(expected_frames=1, timeout_per_frame=duration)

        if not rx_stats['successful_frames']:
            raise RuntimeError("Failed to receive challenge")

        challenge = rx_stats['recovered_data']
        print(f"Received challenge: {challenge.hex()}")
        return challenge

    def compute_and_transmit_response(self, challenge: bytes):
        """
        iPhone: Compute HMAC response and transmit back via protocol layer
        """
        print("=== COMPUTING AND TRANSMITTING RESPONSE ===")

        response = self.auth_protocol.process_challenge(challenge)
        print(f"Response: {response.hex()}")

        # Transmit via EnhancedFSK — applies framing + CRC-16 automatically
        print("Transmitting response acoustically (with protocol layer)...")
        self.fsk.transmit_data_with_protocol(response)

        return response

    def receive_and_verify_response(self, duration=None) -> bool:
        """
        Laptop: Receive response via protocol layer and verify authentication
        """
        print("=== RECEIVING AND VERIFYING RESPONSE ===")

        # Response is 32 bytes + protocol overhead (5 bytes) = 37 bytes = 296 bits
        if duration is None:
            frame_bits = (32 + 5) * 8
            duration = frame_bits * self.fsk.symbol_duration + 1.0

        print(f"Recording for {duration:.1f} seconds...")
        rx_stats = self.fsk.receive_data_with_protocol(expected_frames=1, timeout_per_frame=duration)

        if not rx_stats['successful_frames']:
            print("Failed to receive response")
            return False

        received_response = rx_stats['recovered_data']
        print(f"Received response: {received_response.hex()}")

        return self.auth_protocol.verify_authentication(received_response)
    
    def authenticate_with_handshake(self):
        """
        Laptop: Full authentication with handshaking protocol
        
        Flow:
        1. Send READY tone and wait for ACK
        2. Send challenge
        3. Receive and verify response
        4. Send ACK/NACK confirmation
        
        Returns:
            True if authentication successful, False otherwise
        """
        print("=== ACOUSTIC AUTHENTICATION WITH HANDSHAKING ===")
        
        try:
            # Step 1: Handshake - send READY and wait for ACK
            print("\n--- Step 1: Establishing Connection ---")
            max_attempts = 15  # Try for 30 seconds (15 attempts * 2s)
            connected = False
            
            for attempt in range(max_attempts):
                print(f"\nAttempt {attempt + 1}/{max_attempts}")
                self.send_ready_tone()
                time.sleep(0.5)  # Brief pause
                
                if self.listen_for_ack(timeout=2.0):
                    connected = True
                    break
                    
                print("No ACK received, retrying...")
                time.sleep(0.5)
            
            if not connected:
                print("❌ Connection failed - iPhone did not respond")
                return False
            
            print("✅ Connection established")
            time.sleep(0.5)  # Brief pause before challenge
            
            # Step 2: Send challenge
            print("\n--- Step 2: Sending Challenge ---")
            challenge = self.transmit_challenge()
            time.sleep(0.5)
            
            # Step 3: Receive and verify response
            print("\n--- Step 3: Receiving Response ---")
            success = self.receive_and_verify_response()
            time.sleep(0.5)
            
            # Step 4: Send confirmation
            print("\n--- Step 4: Sending Confirmation ---")
            if success:
                self.send_ack_tone()
                print("\n🔓 ACCESS GRANTED - Authentication Successful!")
            else:
                self.send_nack_tone()
                print("\n🔒 ACCESS DENIED - Authentication Failed!")
            
            return success
            
        except Exception as e:
            print(f"\n❌ Authentication error: {e}")
            try:
                self.send_nack_tone()
            except:
                pass
            return False
    
    def full_authentication_test(self):
        """
        Test complete authentication cycle
        Simulates laptop <-> iPhone communication
        Full stack: HMAC-SHA256 -> Protocol Layer (framing + CRC-16) -> FSK audio
        """
        print("=== FULL ACOUSTIC AUTHENTICATION TEST ===")

        try:
            # Step 1: Laptop generates and transmits challenge
            challenge = self.transmit_challenge()
            time.sleep(0.1)  # Reduced delay

            # Step 2: iPhone computes and transmits response
            print("\n--- Simulating iPhone Response ---")
            response = self.compute_and_transmit_response(challenge)
            time.sleep(0.1)  # Reduced delay

            # Step 3: Laptop verifies response directly (simulation)
            print("\n--- Simulating Laptop Verification ---")
            success = self.auth_protocol.verify_authentication(response)

            print("\n=== AUTHENTICATION RESULT ===")
            if success:
                print("🔓 ACCESS GRANTED - Authentication Successful!")
            else:
                print("🔒 ACCESS DENIED - Authentication Failed!")

            return success

        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        self.fsk.cleanup()
        self.tone_utils.cleanup()

def test_acoustic_authentication():
    """Test the complete acoustic authentication system with handshaking"""
    
    # Create authenticator with shared key
    authenticator = AcousticAuthenticator()
    
    try:
        # Run authentication with handshaking
        print("\n" + "="*60)
        print("ACOUSTIC AUTHENTICATION SYSTEM")
        print("Press 'Authenticate' on iPhone when ready")
        print("="*60 + "\n")
        
        success = authenticator.authenticate_with_handshake()
        
        print(f"\n=== TEST SUMMARY ===")
        print(f"Acoustic Authentication: {'PASSED' if success else 'FAILED'}")
        
        if success:
            print("\n✓ COMPLETE SYSTEM WORKING!")
            print("- Handshaking protocol ✓")
            print("- FSK audio transmission ✓")
            print("- HMAC-SHA256 cryptography ✓") 
            print("- Challenge-response protocol ✓")
            print("- Confirmation feedback ✓")
        
        return success
        
    finally:
        authenticator.cleanup()

if __name__ == "__main__":
    test_acoustic_authentication()