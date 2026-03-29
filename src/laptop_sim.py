"""
LAPTOP SIMULATOR (file-based channel)
Terminal 1: python laptop_sim.py
Terminal 2: python iphone_sim.py
"""

import sys
import os
import time
import hmac
import hashlib

sys.path.insert(0, os.path.dirname(__file__))
from sim_channel import *
from sim_channel import safe_remove
from crypto_core import AuthenticationProtocol

SHARED_KEY   = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0')
SYNC_PATTERN = b'1010101010101010'
MAX_RETRIES  = 3

T0 = None

def ts():
    return f"[t={time.time()-T0:6.2f}s]"

def log(msg):
    print(f"{ts()} [LAPTOP] {msg}", flush=True)

def run_laptop():
    global T0
    T0 = time.time()

    log("=== LAPTOP SIMULATOR STARTED ===")
    log(f"Shared key: {SHARED_KEY.hex()[:16]}...")
    log("Resetting channel...")
    reset_channel()
    log("Channel ready. Starting protocol...\n")

    auth = AuthenticationProtocol(SHARED_KEY)
    auth.session_timeout = 120

    # ── PHASE 1: BEACON ──────────────────────────────────────────────
    log("══ PHASE 1: BEACON ══")
    connected = False
    for attempt in range(20):
        log(f"Beacon attempt {attempt+1}/20: writing READY flag...")
        t = time.time()
        write_flag(READY_FLAG)
        log(f"  READY flag written at {ts()}")

        log(f"  Waiting for ACK flag...")
        found, elapsed = wait_for(ACK_FLAG, timeout=3.0, label="ACK")
        if found:
            log(f"  ✅ ACK received after {elapsed:.3f}s")
            safe_remove(ACK_FLAG)
            connected = True
            break
        else:
            log(f"  ❌ No ACK after {elapsed:.3f}s, retrying...")
            if os.path.exists(READY_FLAG):
                safe_remove(READY_FLAG)

    if not connected:
        log("❌ BEACON FAILED")
        return False

    log("✅ PHASE 1 COMPLETE - iPhone connected\n")

    # ── PHASE 2: SYNC ────────────────────────────────────────────────
    log("══ PHASE 2: SYNC ══")
    sync_acked = False
    for attempt in range(MAX_RETRIES):
        log(f"Sync attempt {attempt+1}/{MAX_RETRIES}: writing sync pattern...")
        t = time.time()
        write_bytes(SYNC_BIN, SYNC_PATTERN)
        log(f"  Sync written in {time.time()-t:.3f}s")

        log(f"  Waiting for SYNC_ACK...")
        found, elapsed = wait_for(SYNC_ACK_FLAG, timeout=10.0)
        if found:
            log(f"  ✅ SYNC_ACK received after {elapsed:.3f}s")
            safe_remove(SYNC_ACK_FLAG)
            sync_acked = True
            break
        else:
            log(f"  ❌ No SYNC_ACK after {elapsed:.3f}s, retrying...")
            if os.path.exists(SYNC_BIN):
                safe_remove(SYNC_BIN)

    if not sync_acked:
        log("❌ SYNC FAILED")
        return False

    log("✅ PHASE 2 COMPLETE\n")

    # ── SLOT 1: CHALLENGE ────────────────────────────────────────────
    log("══ SLOT 1: CHALLENGE ══")
    challenge = auth.initiate_authentication()
    log(f"Challenge generated: {challenge.hex()}")

    challenge_acked = False
    for attempt in range(MAX_RETRIES):
        log(f"Challenge attempt {attempt+1}/{MAX_RETRIES}: writing challenge...")
        t = time.time()
        write_bytes(CHALLENGE_BIN, challenge)
        log(f"  Challenge written in {time.time()-t:.3f}s")

        log(f"  Waiting for CHALLENGE_ACK...")
        found, elapsed = wait_for(CHALLENGE_ACK_FLAG, timeout=10.0)
        if found:
            log(f"  ✅ CHALLENGE_ACK received after {elapsed:.3f}s")
            safe_remove(CHALLENGE_ACK_FLAG)
            challenge_acked = True
            break
        else:
            log(f"  ❌ No CHALLENGE_ACK after {elapsed:.3f}s, retrying...")
            if os.path.exists(CHALLENGE_BIN):
                safe_remove(CHALLENGE_BIN)

    if not challenge_acked:
        log("❌ CHALLENGE FAILED")
        return False

    log("✅ SLOT 1 COMPLETE\n")

    # ── SLOT 2: RECEIVE RESPONSE ─────────────────────────────────────
    log("══ SLOT 2: RECEIVE RESPONSE ══")
    log("Waiting for response...")
    t = time.time()
    found, elapsed = wait_for(RESPONSE_BIN, timeout=15.0)
    if not found:
        log(f"❌ No response after {elapsed:.3f}s")
        return False

    response = read_bytes(RESPONSE_BIN)
    safe_remove(RESPONSE_BIN)
    log(f"✅ Response received after {elapsed:.3f}s: {response.hex()}")

    # Send ACK after response
    log("Writing RESPONSE_ACK...")
    write_flag(RESPONSE_ACK_FLAG)
    log("✅ SLOT 2 COMPLETE\n")

    # ── SLOT 3: VERIFY AND RESULT ────────────────────────────────────
    log("══ SLOT 3: VERIFY AND RESULT ══")
    t = time.time()
    success = auth.verify_authentication(response)
    log(f"Verification took {time.time()-t:.3f}s → {'✅ SUCCESS' if success else '❌ FAILED'}")

    result = {'success': success}
    write_json(RESULT_FLAG, result)
    log(f"Result written: {result}")

    if success:
        log("🔓 ACCESS GRANTED")
    else:
        log("🔒 ACCESS DENIED")

    log(f"\n=== TOTAL TIME: {time.time()-T0:.2f}s ===")
    return success

if __name__ == '__main__':
    result = run_laptop()
    sys.exit(0 if result else 1)
