#!/usr/bin/env python3
"""
Noise Testing Script
Test authentication under different ambient noise conditions
"""

import time
import json
from datetime import datetime
from acoustic_auth import AcousticAuthenticator

def run_noise_test(noise_level, num_trials=10):
    """
    Run authentication tests under specific noise conditions
    
    Args:
        noise_level: Description of noise environment
        num_trials: Number of authentication attempts
    
    Returns:
        dict: Test results
    """
    results = {
        'noise_level': noise_level,
        'num_trials': num_trials,
        'successes': 0,
        'failures': 0,
        'times': [],
        'sync_failures': 0,
        'decode_failures': 0,
        'verify_failures': 0,
        'errors': []
    }
    
    print(f"\n{'='*60}")
    print(f"Testing in: {noise_level}")
    print(f"{'='*60}")
    input("Press Enter when environment is ready...")
    
    for trial in range(1, num_trials + 1):
        print(f"\n--- Trial {trial}/{num_trials} ---")
        
        try:
            auth = AcousticAuthenticator()
            start_time = time.time()
            
            # Run full authentication with detailed error tracking
            print("Running beacon...")
            if not auth.run_beacon():
                results['sync_failures'] += 1
                raise RuntimeError("Beacon failed - sync issue")
            
            print("Sending sync...")
            auth.send_sync()
            
            print("Sending challenge...")
            challenge = auth.send_challenge()
            
            print("Receiving response...")
            try:
                response = auth.receive_response()
            except Exception as e:
                results['decode_failures'] += 1
                raise RuntimeError(f"Decode failed: {e}")
            
            print("Verifying...")
            success = auth.auth_protocol.verify_authentication(response)
            
            elapsed = time.time() - start_time
            
            if success:
                results['successes'] += 1
                results['times'].append(elapsed)
                print(f"✓ SUCCESS ({elapsed:.1f}s)")
            else:
                results['failures'] += 1
                results['verify_failures'] += 1
                print(f"✗ FAILED - Invalid response ({elapsed:.1f}s)")
            
            auth.send_result(success)
            auth.cleanup()
            
        except Exception as e:
            results['failures'] += 1
            results['errors'].append(str(e))
            print(f"✗ ERROR: {e}")
        
        # Wait between trials
        if trial < num_trials:
            time.sleep(2)
    
    # Calculate statistics
    success_rate = (results['successes'] / num_trials) * 100
    avg_time = sum(results['times']) / len(results['times']) if results['times'] else 0
    
    results['success_rate'] = success_rate
    results['avg_time'] = avg_time
    
    print(f"\n{'='*60}")
    print(f"Results in {noise_level}:")
    print(f"  Success Rate: {success_rate:.1f}% ({results['successes']}/{num_trials})")
    print(f"  Average Time: {avg_time:.1f}s")
    print(f"  Sync Failures: {results['sync_failures']}")
    print(f"  Decode Failures: {results['decode_failures']}")
    print(f"  Verify Failures: {results['verify_failures']}")
    print(f"{'='*60}")
    
    return results


def main():
    """Run noise tests in different environments"""
    
    # Test environments
    environments = [
        "Quiet room (library/bedroom)",
        "Moderate noise (office with conversation)",
        "High noise (cafe/open office)"
    ]
    
    trials_per_env = 10
    all_results = []
    
    print("="*60)
    print("ACOUSTIC AUTHENTICATION - NOISE TESTING")
    print("="*60)
    print(f"Testing {len(environments)} environments with {trials_per_env} trials each")
    print("\nEnvironments:")
    for i, env in enumerate(environments, 1):
        print(f"  {i}. {env}")
    print("="*60)
    print("\nIMPORTANT: Keep distance constant at 50cm for all tests")
    print("="*60)
    
    for env in environments:
        results = run_noise_test(env, trials_per_env)
        all_results.append(results)
        
        # Save intermediate results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"noise_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {filename}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY - Noise Level vs Success Rate")
    print("="*60)
    print(f"{'Environment':<40} {'Success Rate':<15}")
    print("-"*60)
    for r in all_results:
        print(f"{r['noise_level']:<40} {r['success_rate']:<14.1f}%")
    print("="*60)
    
    # Print failure analysis
    print("\nFAILURE ANALYSIS")
    print("="*60)
    print(f"{'Environment':<40} {'Sync':<8} {'Decode':<8} {'Verify':<8}")
    print("-"*60)
    for r in all_results:
        print(f"{r['noise_level']:<40} {r['sync_failures']:<8} {r['decode_failures']:<8} {r['verify_failures']:<8}")
    print("="*60)


if __name__ == "__main__":
    main()
