import time
from crypto_core import AuthenticationProtocol
from enhanced_fsk import EnhancedFSK
from tone_utils import ToneUtils

SHARED_KEY = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0')
SYNC_PATTERN = '1010101010101010'  # 16-bit fixed sync pattern

class AcousticAuthenticator:
    """
    Redesigned acoustic authentication system

    Protocol flow:
    Phase 1 - Beacon:
        Laptop broadcasts READY (11kHz, 1s) repeatedly
        iPhone detects in real-time chunks, responds with ACK (13kHz, 1s)
        Laptop detects ACK, moves to Phase 2

    Phase 2 - Sync:
        Laptop sends FSK sync packet (16 bits fixed pattern)
        iPhone decodes sync, knows challenge starts immediately after

    Phase 3 - Data slots:
        Slot 1: Laptop sends FSK challenge (32 bits)
        Slot 2: iPhone sends FSK response (64 bits truncated HMAC)
        Slot 3: Laptop sends READY (11kHz) = success, silence = fail
    """

    def __init__(self):
        self.auth_protocol = AuthenticationProtocol(SHARED_KEY)
        self.auth_protocol.session_timeout = 60
        self.fsk = EnhancedFSK()
        self.tone_utils = ToneUtils()

        self.READY_FREQ       = 11000.0  # 11 kHz - READY beacon
        self.ACK_FREQ         = 13000.0  # 13 kHz - ACK from iPhone
        self.TONE_DURATION    = 1.0      # 1s for beacon/ACK
        self.SUCCESS_DURATION = 1.0      # 1s for result tone

        # Slot durations (symbols * 100ms)
        self.SYNC_DURATION      = (7 + 16) * self.fsk.symbol_duration  # 2.3s
        self.CHALLENGE_DURATION = (7 + 32) * self.fsk.symbol_duration  # 3.9s
        self.RESPONSE_DURATION  = (7 + 64) * self.fsk.symbol_duration  # 7.1s

    # -- Phase 1: Beacon ------------------------------------------------

    def run_beacon(self, max_attempts=20):
        """Broadcast READY beacon until iPhone ACKs"""
        print('=== PHASE 1: BEACON ===')
        for attempt in range(max_attempts):
            print(f'Attempt {attempt+1}/{max_attempts}: sending READY beacon (11kHz)...')
            self.tone_utils.play_tone(self.READY_FREQ, self.TONE_DURATION)

            # Listen for ACK during 3s window
            print('Listening for ACK (13kHz)...')
            signal = self.tone_utils.record_audio(3.0)
            if self.tone_utils.detect_tone(signal, self.ACK_FREQ, threshold=10.0):
                print('✅ ACK detected - iPhone connected')
                return True

            print('No ACK, retrying...')

        print('❌ Beacon failed - no response from iPhone')
        return False

    # -- Phase 2: Sync --------------------------------------------------

    def send_sync(self):
        """Send FSK sync packet so iPhone knows challenge is coming"""
        print('=== PHASE 2: SYNC ===')
        print(f'Sending sync pattern: {SYNC_PATTERN}')
        self.fsk.transmit_data(SYNC_PATTERN)
        print('✅ Sync sent')
        # Wait for iPhone ACK before sending challenge
        print('Listening for ACK after sync...')
        signal = self.tone_utils.record_audio(5.0)
        if not self.tone_utils.detect_tone(signal, self.ACK_FREQ, threshold=10.0):
            raise RuntimeError('No ACK received after sync')
        print('✅ ACK received - iPhone ready for challenge')

    def send_challenge(self):
        """Send 32-bit FSK challenge"""
        print('=== SLOT 1: CHALLENGE ===')
        challenge = self.auth_protocol.initiate_authentication()
        print(f'Challenge: {challenge.hex()}')
        bits = ''.join(format(b, '08b') for b in challenge)
        self.fsk.transmit_data(bits)
        print('✅ Challenge sent')
        # Wait for iPhone ACK before recording response
        print('Listening for ACK after challenge...')
        signal = self.tone_utils.record_audio(5.0)
        if not self.tone_utils.detect_tone(signal, self.ACK_FREQ, threshold=10.0):
            raise RuntimeError('No ACK received after challenge')
        print('✅ ACK received - iPhone ready to respond')
        return challenge

    # -- Phase 3: Data slots --------------------------------------------

    def receive_response(self):
        """Receive 64-bit FSK response from iPhone"""
        print('=== SLOT 2: RECEIVING RESPONSE ===')
        duration = self.RESPONSE_DURATION + 2.0
        print(f'Recording for {duration:.1f}s...')
        signal = self.fsk.record_data(duration)
        bits = self.fsk.decode_signal(signal, 64)
        bits = (bits + '0' * 64)[:64]
        response = bytes(int(bits[i:i+8], 2) for i in range(0, 64, 8))
        print(f'Received response: {response.hex()}')
        # Send ACK to iPhone so it knows response was received
        print('Sending ACK after response...')
        self.tone_utils.play_tone(self.READY_FREQ, self.TONE_DURATION)
        print('✅ ACK sent - iPhone can now listen for result')
        return response

    def send_result(self, success):
        """Send result: READY tone = success, silence = fail"""
        print('=== SLOT 3: RESULT ===')
        if success:
            print('📡 Sending SUCCESS tone (11kHz)...')
            self.tone_utils.play_tone(self.READY_FREQ, self.SUCCESS_DURATION)
            print('🔓 ACCESS GRANTED')
        else:
            print('🔒 ACCESS DENIED - sending silence')
            time.sleep(self.SUCCESS_DURATION)

    # -- Full authentication flow ---------------------------------------

    def authenticate(self):
        """Run full authentication protocol"""
        print('\n' + '='*60)
        print('ACOUSTIC AUTHENTICATION SYSTEM')
        print('='*60 + '\n')

        try:
            if not self.run_beacon():
                return False

            self.send_sync()
            challenge = self.send_challenge()
            response = self.receive_response()
            success = self.auth_protocol.verify_authentication(response)
            self.send_result(success)

            return success

        except Exception as e:
            print(f'❌ Authentication error: {e}')
            return False

    def cleanup(self):
        self.fsk.cleanup()
        self.tone_utils.cleanup()


if __name__ == '__main__':
    auth = AcousticAuthenticator()
    try:
        auth.authenticate()
    finally:
        auth.cleanup()
