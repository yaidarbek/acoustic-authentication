#!/usr/bin/env python3
"""
Distance Testing Script
Run authentication at different distances and log results
"""

import time
import json
from datetime import datetime
from acoustic_auth import AcousticAuthenticator

def run_distance_test(distance_cm, num_trials=10):
    """
    Run authentication tests at a specific distance
    
    Args:
        distance_cm: Distance between devices in centimeters
        num_trials: Number of authentication attempts
    
    Returns:
        dict: Test results with success rate and timing
    """
    results = {
        'distance_cm': distance_cm,
        'num_trials': num_trials,
        'successes': 0,
        'failures': 0,
        'times': [],
        'errors': []
    }
    
    print(f"\n{'='*60}")
    print(f"Testing at {distance_cm} cm distance")
    print(f"{'='*60}")
    print(f"Position iPhone {distance_cm} cm from laptop")
    input("Press Enter when ready...")
    
    for trial in range(1, num_trials + 1):
        print(f"\n--- Trial {trial}/{num_trials} ---")
        
        try:
            auth = AcousticAuthenticator()
            start_time = time.time()
            
            # Run full authentication
            print("Running beacon...")
            if not auth.run_beacon():
                raise RuntimeError("Beacon failed")
            
            print("Sending sync...")
            auth.send_sync()
            
            print("Sending challenge...")
            challenge = auth.send_challenge()
            
            print("Receiving response...")
            response = auth.receive_response()
            
            print("Verifying...")
            success = auth.auth_protocol.verify_authentication(response)
            
            elapsed = time.time() - start_time
            
            if success:
                results['successes'] += 1
                results['times'].append(elapsed)
                print(f"✓ SUCCESS ({elapsed:.1f}s)")
            else:
                results['failures'] += 1
                print(f"✗ FAILED - Invalid response ({elapsed:.1f}s)")
            
            auth.send_result(success)
            auth.cleanup()
            
        except Exception as e:
            results['failures'] += 1
            results['errors'].append(str(e))
            print(f"✗ ERROR: {e}")
        
        # Wait between trials
        if trial < num_trials:
            print("Waiting 3 seconds before next trial...")
            time.sleep(3)
    
    # Calculate statistics
    success_rate = (results['successes'] / num_trials) * 100
    avg_time = sum(results['times']) / len(results['times']) if results['times'] else 0
    
    results['success_rate'] = success_rate
    results['avg_time'] = avg_time
    
    print(f"\n{'='*60}")
    print(f"Results at {distance_cm} cm:")
    print(f"  Success Rate: {success_rate:.1f}% ({results['successes']}/{num_trials})")
    print(f"  Average Time: {avg_time:.1f}s")
    print(f"{'='*60}")
    
    return results


def main():
    """Run distance tests at multiple distances"""
    
    # Test distances (in cm)
    distances = [10, 25, 50, 75, 100]
    trials_per_distance = 10
    
    all_results = []
    
    print("="*60)
    print("ACOUSTIC AUTHENTICATION - DISTANCE TESTING")
    print("="*60)
    print(f"Testing {len(distances)} distances with {trials_per_distance} trials each")
    print(f"Distances: {distances} cm")
    print("="*60)
    
    for distance in distances:
        results = run_distance_test(distance, trials_per_distance)
        all_results.append(results)
        
        # Save intermediate results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"distance_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {filename}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY - Distance vs Success Rate")
    print("="*60)
    print(f"{'Distance (cm)':<15} {'Success Rate':<15} {'Avg Time (s)':<15}")
    print("-"*60)
    for r in all_results:
        print(f"{r['distance_cm']:<15} {r['success_rate']:<14.1f}% {r['avg_time']:<14.1f}s")
    print("="*60)


if __name__ == "__main__":
    main()
