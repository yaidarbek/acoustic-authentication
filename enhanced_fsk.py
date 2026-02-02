import numpy as np
import pyaudio
import time
from protocol_layer import ProtocolLayer, AudioFrame
from working_fsk import WorkingFSK

class EnhancedFSK(WorkingFSK):
    """
    Enhanced FSK with protocol layer integration
    Adds frame structure, CRC error detection, and reliability improvements
    """
    
    def __init__(self):
        super().__init__()
        self.protocol = ProtocolLayer()
        
    def bytes_to_bits(self, data: bytes) -> str:
        """Convert bytes to binary string"""
        return ''.join(format(byte, '08b') for byte in data)
    
    def bits_to_bytes(self, bits: str) -> bytes:
        """Convert binary string to bytes"""
        # Pad to multiple of 8
        while len(bits) % 8 != 0:
            bits += '0'
        
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    
    def transmit_data_with_protocol(self, data: bytes) -> dict:
        """
        Transmit data using protocol layer
        Returns transmission statistics
        """
        print(f"=== Enhanced FSK Transmission ===")
        print(f"Data to transmit: {len(data)} bytes")
        
        # Prepare frames using protocol layer
        frames = self.protocol.prepare_transmission(data)
        print(f"Split into {len(frames)} frame(s)")
        
        transmission_stats = {
            'total_frames': len(frames),
            'total_bytes': sum(len(frame) for frame in frames),
            'original_bytes': len(data),
            'overhead_bytes': sum(len(frame) for frame in frames) - len(data),
            'frame_details': []
        }
        
        # Transmit each frame
        for i, frame in enumerate(frames):
            print(f"\nTransmitting frame {i+1}/{len(frames)}:")
            
            # Get frame info for statistics
            frame_info = self.protocol.get_frame_info(frame)
            print(f"  Frame info: {frame_info}")
            
            # Convert frame to bits
            frame_bits = self.bytes_to_bits(frame)
            print(f"  Frame size: {len(frame)} bytes = {len(frame_bits)} bits")
            
            # Transmit via FSK
            duration = self.transmit_data(frame_bits)
            
            transmission_stats['frame_details'].append({
                'frame_number': i + 1,
                'frame_bytes': len(frame),
                'frame_bits': len(frame_bits),
                'transmission_duration': duration,
                'frame_info': frame_info
            })
            
            # Brief pause between frames
            if i < len(frames) - 1:
                time.sleep(0.1)
        
        print(f"\nTransmission complete:")
        print(f"  Original data: {transmission_stats['original_bytes']} bytes")
        print(f"  Total transmitted: {transmission_stats['total_bytes']} bytes")
        print(f"  Protocol overhead: {transmission_stats['overhead_bytes']} bytes")
        print(f"  Overhead ratio: {transmission_stats['overhead_bytes']/transmission_stats['original_bytes']*100:.1f}%")
        
        return transmission_stats
    
    def receive_data_with_protocol(self, expected_frames: int = 1, timeout_per_frame: float = 5.0) -> dict:
        """
        Receive data using protocol layer
        Returns reception results
        """
        print(f"\n=== Enhanced FSK Reception ===")
        print(f"Expecting {expected_frames} frame(s)")
        
        reception_stats = {
            'expected_frames': expected_frames,
            'received_frames': 0,
            'successful_frames': 0,
            'failed_frames': 0,
            'recovered_data': b'',
            'frame_results': [],
            'errors': []
        }
        
        for frame_num in range(expected_frames):
            print(f"\nReceiving frame {frame_num + 1}/{expected_frames}:")
            
            try:
                # Record audio for this frame
                # Estimate frame duration based on typical frame size
                estimated_bits = 200 * 8  # Assume ~200 bytes per frame
                estimated_duration = estimated_bits * self.symbol_duration + 1.0
                record_duration = min(estimated_duration, timeout_per_frame)
                
                print(f"  Recording for {record_duration:.1f} seconds...")
                recorded_signal = self.record_data(record_duration)
                
                # Decode FSK signal to bits
                # Try different bit lengths to find valid frame
                for bit_length in [100, 200, 300, 400, 500]:  # Try different lengths
                    try:
                        frame_bits = self.decode_signal(recorded_signal, bit_length)
                        
                        # Convert bits to bytes
                        frame_bytes = self.bits_to_bytes(frame_bits)
                        
                        # Try to parse as protocol frame
                        success, payload, error = self.protocol.process_received_frame(frame_bytes)
                        
                        if success:
                            print(f"  ✓ Frame decoded successfully ({bit_length} bits)")
                            print(f"  Payload: {len(payload)} bytes")
                            
                            reception_stats['received_frames'] += 1
                            reception_stats['successful_frames'] += 1
                            reception_stats['recovered_data'] += payload
                            
                            frame_info = self.protocol.get_frame_info(frame_bytes)
                            reception_stats['frame_results'].append({
                                'frame_number': frame_num + 1,
                                'success': True,
                                'payload_bytes': len(payload),
                                'frame_info': frame_info,
                                'error': None
                            })
                            break
                            
                    except Exception as decode_error:
                        continue  # Try next bit length
                        
                else:
                    # No valid frame found
                    print(f"  ✗ No valid frame found")
                    reception_stats['received_frames'] += 1
                    reception_stats['failed_frames'] += 1
                    
                    error_msg = "No valid frame detected"
                    reception_stats['errors'].append(error_msg)
                    reception_stats['frame_results'].append({
                        'frame_number': frame_num + 1,
                        'success': False,
                        'payload_bytes': 0,
                        'frame_info': None,
                        'error': error_msg
                    })
                    
            except Exception as e:
                print(f"  ✗ Reception error: {e}")
                reception_stats['failed_frames'] += 1
                reception_stats['errors'].append(str(e))
        
        # Print reception summary
        print(f"\nReception complete:")
        print(f"  Expected frames: {reception_stats['expected_frames']}")
        print(f"  Successful frames: {reception_stats['successful_frames']}")
        print(f"  Failed frames: {reception_stats['failed_frames']}")
        print(f"  Success rate: {reception_stats['successful_frames']/reception_stats['expected_frames']*100:.1f}%")
        print(f"  Recovered data: {len(reception_stats['recovered_data'])} bytes")
        
        return reception_stats
    
    def test_enhanced_transmission(self, test_data: bytes = b"Enhanced FSK Test Data with Protocol Layer!"):
        """Test enhanced FSK with protocol layer"""
        print("=== Enhanced FSK Test ===")
        
        # Transmit data
        tx_stats = self.transmit_data_with_protocol(test_data)
        
        # Wait between transmission and reception
        time.sleep(0.5)
        
        # Receive data
        rx_stats = self.receive_data_with_protocol(
            expected_frames=tx_stats['total_frames'],
            timeout_per_frame=10.0
        )
        
        # Compare results
        success = rx_stats['recovered_data'] == test_data
        
        print(f"\n=== Test Results ===")
        print(f"Original data: {test_data}")
        print(f"Recovered data: {rx_stats['recovered_data']}")
        print(f"Match: {success}")
        
        if success:
            print("🎉 Enhanced FSK test PASSED!")
        else:
            print("❌ Enhanced FSK test FAILED")
            
        return success, tx_stats, rx_stats

def compare_basic_vs_enhanced():
    """Compare basic FSK vs enhanced FSK with protocol layer"""
    print("=== Basic vs Enhanced FSK Comparison ===")
    
    test_data = b"Comparison test data for FSK systems"
    
    # Test basic FSK
    print("\n--- Basic FSK ---")
    basic_fsk = WorkingFSK()
    
    start_time = time.time()
    basic_duration = basic_fsk.transmit_data(''.join(format(byte, '08b') for byte in test_data))
    basic_time = time.time() - start_time
    basic_fsk.cleanup()
    
    print(f"Basic FSK transmission: {basic_time:.2f}s")
    
    # Test enhanced FSK
    print("\n--- Enhanced FSK ---")
    enhanced_fsk = EnhancedFSK()
    
    start_time = time.time()
    tx_stats = enhanced_fsk.transmit_data_with_protocol(test_data)
    enhanced_time = time.time() - start_time
    enhanced_fsk.cleanup()
    
    print(f"Enhanced FSK transmission: {enhanced_time:.2f}s")
    
    # Comparison
    print(f"\n--- Comparison ---")
    print(f"Time overhead: {((enhanced_time - basic_time) / basic_time * 100):.1f}%")
    print(f"Data overhead: {tx_stats['overhead_bytes']} bytes ({tx_stats['overhead_bytes']/len(test_data)*100:.1f}%)")
    print(f"Benefits: Error detection, frame structure, reliability")

if __name__ == "__main__":
    enhanced_fsk = EnhancedFSK()
    
    try:
        # Run enhanced FSK test
        success, tx_stats, rx_stats = enhanced_fsk.test_enhanced_transmission()
        
        # Run comparison
        compare_basic_vs_enhanced()
        
    finally:
        enhanced_fsk.cleanup()