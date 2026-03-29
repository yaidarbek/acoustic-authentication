import time
from crypto_core import AuthenticationProtocol
from enhanced_fsk import EnhancedFSK
from tone_utils import ToneUtils

SHARED_KEY = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0')
SYNC_PATTERN = '1010101010101010'  # 16-bit fixed sync pattern
MAX_RETRIES = 3

class AcousticAuthenticator:
    """
    Redesigned acoustic authentication system

    Protocol flow:
    Phase 1 - Beacon:
        Laptop broadcasts READY (11kHz, 1s) repeatedly
        iPhone detects in real-time chunks, responds with ACK (13kHz, 1s)
        Laptop detects ACK, moves to Phase 2

    Phase 2 - Sync:
        Laptop plays sentinel (5kHz) then sends FSK sync packet
        iPhone detects sentinel, starts recording FSK immediately
        iPhone decodes sync, sends ACK

    Phase 3 - Data slots:
        Slot 1: Laptop plays sentinel then sends FSK challenge (32 bits)
        Slot 2: iPhone sends sentinel then FSK response (64 bits truncated HMAC)
        Slot 3: Laptop sends READY (11kHz) = success, silence = fail
    """

    def __init__(self):
        self.auth_protocol = AuthenticationProtocol(SHARED_KEY)
        self.auth_protocol.session_timeout = 60
        self.fsk = EnhancedFSK()
        self.tone_utils = ToneUtils()

        self.READY_FREQ        = 11000.0  # 11 kHz - READY beacon
        self.ACK_FREQ          = 13000.0  # 13 kHz - ACK from iPhone
        self.SENTINEL_FREQ     = 5000.0   # 5 kHz - start sentinel before FSK
        self.TONE_DURATION     = 1.0      # 1s for beacon/ACK
        self.SENTINEL_DURATION = 0.3      # 0.3s sentinel tone
        self.SUCCESS_DURATION  = 1.0      # 1s for result tone

        # Slot durations (symbols * 150ms)
        self.SYNC_DURATION      = (7 + 16) * self.fsk.symbol_duration
        self.CHALLENGE_DURATION = (7 + 32) * self.fsk.symbol_duration
        self.RESPONSE_DURATION  = (7 + 64) * self.fsk.symbol_duration

    # -- Helpers --------------------------------------------------------

    def _send_sentinel(self):
        """Play sentinel tone before FSK so iPhone knows signal is coming"""
        self.tone_utils.play_tone(self.SENTINEL_FREQ, self.SENTINEL_DURATION)

    def _signal_quality_ok(self, signal) -> bool:
        """Check signal has enough power to be worth decoding"""
        import numpy as np
        max_amp = float(np.max(np.abs(signal)))
        if max_amp < 0.01:
            print(f'[Quality] Signal too weak: max_amp={max_amp:.4f}')
            return False
        return True

    # -- Phase 1: Beacon ------------------------------------------------

    def run_beacon(self, max_attempts=20):
        """Broadcast READY beacon until iPhone ACKs"""
        print('=== PHASE 1: BEACON ===')
        for attempt in range(max_attempts):
            print(f'Attempt {attempt+1}/{max_attempts}: sending READY beacon (11kHz)...')
            self.tone_utils.play_tone(self.READY_FREQ, self.TONE_DURATION)

            print('Listening for ACK (13kHz)...')
            if self.tone_utils.detect_tone_chunked(self.ACK_FREQ, max_duration=3.0, chunk_duration=0.5, threshold=10.0):
                print('✅ ACK detected - iPhone connected')
                # Wait for iPhone to finish playing ACK and switch to record mode
                time.sleep(self.TONE_DURATION + 0.3)
                return True

            print('No ACK, retrying...')

        print('❌ Beacon failed - no response from iPhone')
        return False

    # -- Phase 2: Sync --------------------------------------------------

    def send_sync(self):
        """Send FSK sync packet with sentinel, retry up to MAX_RETRIES times"""
        print('=== PHASE 2: SYNC ===')
        for attempt in range(MAX_RETRIES):
            print(f'Sync attempt {attempt+1}/{MAX_RETRIES}')
            self._send_sentinel()
            self.fsk.transmit_data(SYNC_PATTERN)
            print('✅ Sync sent')
            print('Listening for ACK after sync...')
            if self.tone_utils.detect_tone_chunked(self.ACK_FREQ, max_duration=5.0, chunk_duration=0.5, threshold=10.0):
                print('✅ ACK received - iPhone ready for challenge')
                time.sleep(self.TONE_DURATION + 0.3)
                return
            print(f'No ACK after sync, retrying...')
        raise RuntimeError('No ACK received after sync - max retries exceeded')

    # -- Phase 3: Data slots --------------------------------------------

    def send_challenge(self):
        """Send 32-bit FSK challenge with sentinel, retry up to MAX_RETRIES times"""
        print('=== SLOT 1: CHALLENGE ===')
        challenge = self.auth_protocol.initiate_authentication()
        print(f'Challenge: {challenge.hex()}')
        bits = ''.join(format(b, '08b') for b in challenge)
        for attempt in range(MAX_RETRIES):
            print(f'Challenge attempt {attempt+1}/{MAX_RETRIES}')
            self._send_sentinel()
            self.fsk.transmit_data(bits)
            print('✅ Challenge sent')
            print('Listening for ACK after challenge...')
            if self.tone_utils.detect_tone_chunked(self.ACK_FREQ, max_duration=5.0, chunk_duration=0.5, threshold=10.0):
                print('✅ ACK received - iPhone ready to respond')
                time.sleep(self.TONE_DURATION + 0.3)
                return challenge
            print(f'No ACK after challenge, retrying...')
        raise RuntimeError('No ACK received after challenge - max retries exceeded')

    def receive_response(self):
        """Receive 64-bit FSK response from iPhone"""
        print('=== SLOT 2: RECEIVING RESPONSE ===')
        duration = self.RESPONSE_DURATION + 2.0
        print(f'Recording for {duration:.1f}s...')
        signal = self.fsk.record_data(duration)

        if not self._signal_quality_ok(signal):
            raise RuntimeError('Response signal too weak')

        bits = self.fsk.decode_signal(signal, 64)
        bits = (bits + '0' * 64)[:64]
        response = bytes(int(bits[i:i+8], 2) for i in range(0, 64, 8))
        print(f'Received response: {response.hex()}')
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
