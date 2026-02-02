import struct
from typing import Optional, Tuple
from dataclasses import dataclass

class CRC16:
    """
    CRC-16-CCITT implementation for error detection
    Polynomial: 0x1021 (x^16 + x^12 + x^5 + 1)
    """
    
    def __init__(self):
        self.polynomial = 0x1021
        self.initial_value = 0xFFFF
        
    def calculate(self, data: bytes) -> int:
        """Calculate CRC-16 checksum for data"""
        crc = self.initial_value
        
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ self.polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF
                
        return crc
    
    def verify(self, data: bytes, expected_crc: int) -> bool:
        """Verify data integrity using CRC"""
        calculated_crc = self.calculate(data)
        return calculated_crc == expected_crc

@dataclass
class FrameHeader:
    """Frame header structure"""
    frame_type: int     # 4 bits - frame type (0=data, 1=ack, etc.)
    sequence: int       # 4 bits - sequence number for ordering
    length: int         # 8 bits - payload length (0-255 bytes)
    
    def to_bytes(self) -> bytes:
        """Convert header to bytes"""
        # Pack type and sequence into first byte, length into second byte
        type_seq = (self.frame_type << 4) | (self.sequence & 0x0F)
        return struct.pack('BB', type_seq, self.length)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'FrameHeader':
        """Create header from bytes"""
        if len(data) < 2:
            raise ValueError("Header data too short")
            
        type_seq, length = struct.unpack('BB', data[:2])
        frame_type = (type_seq >> 4) & 0x0F
        sequence = type_seq & 0x0F
        
        return cls(frame_type, sequence, length)

class AudioFrame:
    """
    Structured frame for acoustic transmission
    
    Frame Format:
    [Preamble: 8 bits] [Header: 16 bits] [Payload: 0-255 bytes] [CRC: 16 bits]
    
    - Preamble: 0xAA (10101010) for synchronization
    - Header: Frame type, sequence, length
    - Payload: Actual data
    - CRC: Error detection checksum
    """
    
    PREAMBLE = 0xAA  # 10101010 pattern for sync
    MAX_PAYLOAD_SIZE = 255
    
    def __init__(self):
        self.header = None
        self.payload = b''
        self.crc_calculator = CRC16()
        
    def create_data_frame(self, payload: bytes, sequence: int = 0) -> bytes:
        """Create a data frame with payload"""
        if len(payload) > self.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload too large: {len(payload)} > {self.MAX_PAYLOAD_SIZE}")
            
        # Create header
        self.header = FrameHeader(
            frame_type=0,  # Data frame
            sequence=sequence & 0x0F,  # 4-bit sequence number
            length=len(payload)
        )
        
        self.payload = payload
        
        # Build frame without CRC first
        frame_data = bytes([self.PREAMBLE]) + self.header.to_bytes() + self.payload
        
        # Calculate CRC over header + payload
        crc_data = self.header.to_bytes() + self.payload
        crc = self.crc_calculator.calculate(crc_data)
        
        # Add CRC to frame (big-endian 16-bit)
        frame_with_crc = frame_data + struct.pack('>H', crc)
        
        return frame_with_crc
    
    def parse_frame(self, frame_data: bytes) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Parse received frame data
        
        Returns:
            (success, payload, error_message)
        """
        try:
            # Check minimum frame size
            if len(frame_data) < 5:  # preamble + header + crc
                return False, None, "Frame too short"
            
            # Check preamble
            if frame_data[0] != self.PREAMBLE:
                return False, None, "Invalid preamble"
            
            # Parse header
            try:
                header = FrameHeader.from_bytes(frame_data[1:3])
            except ValueError as e:
                return False, None, f"Header error: {e}"
            
            # Check frame length consistency
            expected_frame_length = 1 + 2 + header.length + 2  # preamble + header + payload + crc
            if len(frame_data) != expected_frame_length:
                return False, None, f"Length mismatch: expected {expected_frame_length}, got {len(frame_data)}"
            
            # Extract payload and CRC
            payload = frame_data[3:3+header.length]
            crc_bytes = frame_data[3+header.length:3+header.length+2]
            
            if len(crc_bytes) != 2:
                return False, None, "Missing CRC"
            
            received_crc = struct.unpack('>H', crc_bytes)[0]
            
            # Verify CRC
            crc_data = frame_data[1:3+header.length]  # header + payload
            if not self.crc_calculator.verify(crc_data, received_crc):
                return False, None, "CRC verification failed"
            
            return True, payload, None
            
        except Exception as e:
            return False, None, f"Parse error: {e}"
    
    def create_ack_frame(self, sequence: int) -> bytes:
        """Create acknowledgment frame"""
        header = FrameHeader(
            frame_type=1,  # ACK frame
            sequence=sequence & 0x0F,
            length=0  # No payload
        )
        
        frame_data = bytes([self.PREAMBLE]) + header.to_bytes()
        crc = self.crc_calculator.calculate(header.to_bytes())
        
        return frame_data + struct.pack('>H', crc)

class ProtocolLayer:
    """
    High-level protocol management
    Handles framing, sequencing, and reliability
    """
    
    def __init__(self):
        self.frame_handler = AudioFrame()
        self.tx_sequence = 0
        self.rx_sequence = 0
        
    def prepare_transmission(self, data: bytes) -> list[bytes]:
        """
        Prepare data for transmission
        Splits large data into multiple frames if needed
        
        Returns list of frames ready for FSK transmission
        """
        frames = []
        
        # Split data into chunks if too large
        max_chunk_size = AudioFrame.MAX_PAYLOAD_SIZE
        
        for i in range(0, len(data), max_chunk_size):
            chunk = data[i:i+max_chunk_size]
            frame = self.frame_handler.create_data_frame(chunk, self.tx_sequence)
            frames.append(frame)
            
            self.tx_sequence = (self.tx_sequence + 1) % 16  # 4-bit sequence
            
        return frames
    
    def process_received_frame(self, frame_data: bytes) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Process received frame
        
        Returns:
            (success, payload_data, error_message)
        """
        success, payload, error = self.frame_handler.parse_frame(frame_data)
        
        if success:
            # TODO: Add sequence number validation for ordering
            # TODO: Add duplicate detection
            pass
            
        return success, payload, error
    
    def get_frame_info(self, frame_data: bytes) -> dict:
        """Get frame information for debugging"""
        if len(frame_data) < 3:
            return {"error": "Frame too short"}
            
        try:
            preamble = frame_data[0]
            header = FrameHeader.from_bytes(frame_data[1:3])
            
            return {
                "preamble": f"0x{preamble:02X}",
                "frame_type": header.frame_type,
                "sequence": header.sequence,
                "payload_length": header.length,
                "total_length": len(frame_data)
            }
        except Exception as e:
            return {"error": str(e)}

def test_protocol_layer():
    """Test the protocol layer implementation"""
    print("=== Protocol Layer Test ===")
    
    protocol = ProtocolLayer()
    
    # Test 1: Basic frame creation and parsing
    print("\n1. Testing basic frame operations...")
    test_data = b"Hello, World!"
    
    frames = protocol.prepare_transmission(test_data)
    print(f"Created {len(frames)} frame(s) for {len(test_data)} bytes")
    
    # Parse the frame back
    success, recovered_data, error = protocol.process_received_frame(frames[0])
    
    print(f"Frame parsing: {'SUCCESS' if success else 'FAILED'}")
    if success:
        print(f"Original:  {test_data}")
        print(f"Recovered: {recovered_data}")
        print(f"Match:     {test_data == recovered_data}")
    else:
        print(f"Error: {error}")
    
    # Test 2: CRC error detection
    print("\n2. Testing CRC error detection...")
    frame = frames[0]
    
    # Corrupt one byte in the middle
    corrupted_frame = bytearray(frame)
    corrupted_frame[len(frame)//2] ^= 0x01  # Flip one bit
    
    success, _, error = protocol.process_received_frame(bytes(corrupted_frame))
    print(f"Corrupted frame detection: {'SUCCESS' if not success else 'FAILED'}")
    print(f"Error message: {error}")
    
    # Test 3: Large data splitting
    print("\n3. Testing large data handling...")
    large_data = b"A" * 300  # Larger than max frame size
    
    frames = protocol.prepare_transmission(large_data)
    print(f"Large data split into {len(frames)} frames")
    
    # Reconstruct data
    reconstructed = b""
    for frame in frames:
        success, payload, error = protocol.process_received_frame(frame)
        if success:
            reconstructed += payload
        else:
            print(f"Frame error: {error}")
            break
    
    print(f"Reconstruction: {'SUCCESS' if reconstructed == large_data else 'FAILED'}")
    print(f"Original size: {len(large_data)}, Reconstructed: {len(reconstructed)}")
    
    # Test 4: Frame information
    print("\n4. Frame structure analysis...")
    frame_info = protocol.get_frame_info(frames[0])
    print("Frame info:", frame_info)
    
    return test_data == recovered_data and not success  # Should detect corruption

if __name__ == "__main__":
    test_protocol_layer()