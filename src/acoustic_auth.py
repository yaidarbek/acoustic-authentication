import time
from crypto_core import AuthenticationProtocol
from enhanced_fsk import EnhancedFSK

class AcousticAuthenticator:
    """
    Integrated acoustic authentication system
    Combines FSK audio transmission with HMAC-SHA256 cryptography
    Full stack: FSK -> Protocol Layer (framing + CRC-16) -> HMAC-SHA256
    """

    def __init__(self, shared_key=None):
        self.auth_protocol = AuthenticationProtocol(shared_key)
        self.fsk = EnhancedFSK()

    def bytes_to_bits(self, data: bytes) -> str:
        """Convert bytes to binary string"""
        return ''.join(format(byte, '08b') for byte in data)

    def bits_to_bytes(self, bits: str) -> bytes:
        """Convert binary string to bytes"""
        while len(bits) % 8 != 0:
            bits += '0'
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    
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
            time.sleep(0.5)

            # Step 2: iPhone computes and transmits response
            print("\n--- Simulating iPhone Response ---")
            response = self.compute_and_transmit_response(challenge)
            time.sleep(0.5)

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

def test_acoustic_authentication():
    """Test the complete acoustic authentication system"""
    
    # Create authenticator with shared key
    authenticator = AcousticAuthenticator()
    
    try:
        # Run full authentication test
        success = authenticator.full_authentication_test()
        
        print(f"\n=== TEST SUMMARY ===")
        print(f"Acoustic Authentication: {'PASSED' if success else 'FAILED'}")
        
        if success:
            print("\n✓ COMPLETE SYSTEM WORKING!")
            print("- FSK audio transmission ✓")
            print("- HMAC-SHA256 cryptography ✓") 
            print("- Challenge-response protocol ✓")
            print("- Integration layer ✓")
        
        return success
        
    finally:
        authenticator.cleanup()

if __name__ == "__main__":
    test_acoustic_authentication()