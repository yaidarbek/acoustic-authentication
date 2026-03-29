"""
sim_channel.py - Shared file-based communication channel
Both laptop_sim.py and iphone_sim.py use this to pass messages
"""

import os
import time
import json

CHANNEL_DIR = os.path.join(os.path.dirname(__file__), 'sim_channel')

# Message filenames
READY_FLAG        = os.path.join(CHANNEL_DIR, 'ready.flag')
ACK_FLAG          = os.path.join(CHANNEL_DIR, 'ack.flag')
SYNC_BIN          = os.path.join(CHANNEL_DIR, 'sync.bin')
SYNC_ACK_FLAG     = os.path.join(CHANNEL_DIR, 'sync_ack.flag')
CHALLENGE_BIN     = os.path.join(CHANNEL_DIR, 'challenge.bin')
CHALLENGE_ACK_FLAG= os.path.join(CHANNEL_DIR, 'challenge_ack.flag')
RESPONSE_BIN      = os.path.join(CHANNEL_DIR, 'response.bin')
RESPONSE_ACK_FLAG = os.path.join(CHANNEL_DIR, 'response_ack.flag')
RESULT_FLAG       = os.path.join(CHANNEL_DIR, 'result.flag')

POLL_INTERVAL = 0.05   # 50ms polling
TIMEOUT       = 30.0   # 30s max wait per step

def safe_remove(path, retries=5, delay=0.05):
    """Delete file with retry on Windows permission errors"""
    for _ in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)
            return
        except PermissionError:
            time.sleep(delay)

def reset_channel():
    """Delete all message files to start fresh"""
    for f in [READY_FLAG, ACK_FLAG, SYNC_BIN, SYNC_ACK_FLAG,
              CHALLENGE_BIN, CHALLENGE_ACK_FLAG, RESPONSE_BIN,
              RESPONSE_ACK_FLAG, RESULT_FLAG]:
        safe_remove(f)

def write_bytes(path, data: bytes):
    """Write binary data atomically using temp file + rename"""
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def write_flag(path):
    """Create a flag file atomically"""
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        f.write(str(time.time()))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def read_bytes(path) -> bytes:
    """Read binary data"""
    with open(path, 'rb') as f:
        return f.read()

def write_json(path, data):
    """Write JSON data"""
    with open(path, 'w') as f:
        json.dump(data, f)

def read_json(path):
    """Read JSON data"""
    with open(path, 'r') as f:
        return json.load(f)

def wait_for(path, timeout=TIMEOUT, label=""):
    """
    Poll until file exists or timeout.
    Returns (True, elapsed) if found, (False, elapsed) if timeout.
    """
    start = time.time()
    while True:
        if os.path.exists(path):
            elapsed = time.time() - start
            return True, elapsed
        elapsed = time.time() - start
        if elapsed > timeout:
            return False, elapsed
        time.sleep(POLL_INTERVAL)
