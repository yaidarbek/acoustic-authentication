"""
IPHONE SIMULATOR (file-based channel)
Terminal 1: python laptop_sim.py
Terminal 2: python iphone_sim.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from sim_channel import *
from sim_channel import safe_remove
from crypto_core import CryptographicCore

SHARED_KEY   = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0')
SYNC_PATTERN = b'1010101010101010'
MAX_RETRIES  = 3

T0 = None

def ts():
    return f"[t={time.time()-T0:6.2f}s]"

def log(msg):
    print(f"{ts()} [IPHONE] {msg}", flush=True)

def run_iphone():
    global T0
    T0 = time.time()

    log("=== IPHONE SIMULATOR STARTED ===")
    log(f"Shared key: {SHARED_KEY.hex()[:16]}...")
    log("Waiting for laptop to start...\n")

    crypto = CryptographicCore(SHARED_KEY)

    # ── PHASE 1: DETECT BEACON ───────────────────────────────────────
    log("══ PHASE 1: DETECT BEACON ══")
    log("Waiting for READY flag...")
    t = time.time()
    found, elapsed = wait_for(READY_FLAG, timeout=60.0, label="READY")
    if not found:
        log(f"❌ READY flag not found after {elapsed:.3f}s")
        return False

    log(f"✅ READY detected after {elapsed:.3f}s")
    safe_remove(READY_FLAG)

    # Simulate ACK tone delay (iPhone processing time)
    time.sleep(0.1)
    log("Writing ACK flag...")
    t = time.time()
    write_flag(ACK_FLAG)
    log(f"✅ ACK written in {time.time()-t:.3f}s")
    log("✅ PHASE 1 COMPLETE\n")

    # ── PHASE 2: SYNC ────────────────────────────────────────────────
    log("══ PHASE 2: SYNC ══")
    sync_ok = False
    for attempt in range(MAX_RETRIES):
        log(f"Sync attempt {attempt+1}/{MAX_RETRIES}: waiting for sync...")
        t = time.time()
        found, elapsed = wait_for(SYNC_BIN, timeout=10.0)
        if not found:
            log(f"  ❌ Sync not received after {elapsed:.3f}s")
            continue

        sync_data = read_bytes(SYNC_BIN)
        safe_remove(SYNC_BIN)
        log(f"  Sync received after {elapsed:.3f}s: {sync_data}")
        log(f"  Expected:                          {SYNC_PATTERN}")

        if sync_data == SYNC_PATTERN:
            log(f"  ✅ Sync pattern matched!")
            sync_ok = True
            break
        else:
            log(f"  ❌ Sync mismatch! got={sync_data} expected={SYNC_PATTERN}")

    if not sync_ok:
        log("❌ SYNC FAILED after 3 attempts")
        return False

    # Send SYNC_ACK
    time.sleep(0.1)
    log("Writing SYNC_ACK...")
    write_flag(SYNC_ACK_FLAG)
    log("✅ PHASE 2 COMPLETE\n")

    # ── SLOT 1: RECEIVE CHALLENGE ────────────────────────────────────
    log("══ SLOT 1: RECEIVE CHALLENGE ══")
    challenge = None
    for attempt in range(MAX_RETRIES):
        log(f"Challenge attempt {attempt+1}/{MAX_RETRIES}: waiting for challenge...")
        t = time.time()
        found, elapsed = wait_for(CHALLENGE_BIN, timeout=10.0)
        if not found:
            log(f"  ❌ Challenge not received after {elapsed:.3f}s")
            continue

        challenge = read_bytes(CHALLENGE_BIN)
        safe_remove(CHALLENGE_BIN)
        log(f"  Challenge received after {elapsed:.3f}s: {challenge.hex()}")
        log(f"  Challenge size: {len(challenge)} bytes")

        if len(challenge) == 4:
            log(f"  ✅ Challenge valid!")
            break
        else:
            log(f"  ❌ Wrong challenge size: {len(challenge)}, expected 4")
            challenge = None

    if challenge is None:
        log("❌ CHALLENGE FAILED after 3 attempts")
        return False

    # Send CHALLENGE_ACK
    time.sleep(0.1)
    log("Writing CHALLENGE_ACK...")
    write_flag(CHALLENGE_ACK_FLAG)
    log("✅ SLOT 1 COMPLETE\n")

    # ── COMPUTE RESPONSE ─────────────────────────────────────────────
    log("══ COMPUTING RESPONSE ══")
    t = time.time()
    response = crypto.compute_response(challenge)
    log(f"HMAC computed in {time.time()-t:.3f}s")
    log(f"Response: {response.hex()}")
    log(f"Response size: {len(response)} bytes")

    # ── SLOT 2: TRANSMIT RESPONSE ────────────────────────────────────
    log("\n══ SLOT 2: TRANSMIT RESPONSE ══")
    log("Writing response...")
    t = time.time()
    write_bytes(RESPONSE_BIN, response)
    log(f"Response written in {time.time()-t:.3f}s")

    log("Waiting for RESPONSE_ACK from laptop...")
    t = time.time()
    found, elapsed = wait_for(RESPONSE_ACK_FLAG, timeout=15.0)
    if not found:
        log(f"❌ No RESPONSE_ACK after {elapsed:.3f}s")
        return False

    safe_remove(RESPONSE_ACK_FLAG)
    log(f"✅ RESPONSE_ACK received after {elapsed:.3f}s")
    log("✅ SLOT 2 COMPLETE\n")

    # ── SLOT 3: LISTEN FOR RESULT ────────────────────────────────────
    log("══ SLOT 3: LISTEN FOR RESULT ══")
    log("Waiting for result...")
    t = time.time()
    found, elapsed = wait_for(RESULT_FLAG, timeout=15.0)
    if not found:
        log(f"❌ No result after {elapsed:.3f}s")
        return False

    result = read_json(RESULT_FLAG)
    safe_remove(RESULT_FLAG)
    success = result.get('success', False)
    log(f"Result received after {elapsed:.3f}s: {result}")

    if success:
        log("🔓 ACCESS GRANTED")
    else:
        log("🔒 ACCESS DENIED")

    log(f"\n=== TOTAL TIME: {time.time()-T0:.2f}s ===")
    return success

if __name__ == '__main__':
    result = run_iphone()
    sys.exit(0 if result else 1)
