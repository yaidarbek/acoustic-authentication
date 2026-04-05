import os
import json
from cryptography.fernet import Fernet
from typing import Optional

_SRC_DIR     = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR  = os.path.join(_SRC_DIR, "secure_storage")
STORAGE_INDEX = os.path.join(STORAGE_DIR, "index.json")

class SecureStorage:
    """
    Encrypted file storage that requires acoustic authentication
    """
    
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(Fernet.generate_key() if not encryption_key else 
                            self._derive_fernet_key(encryption_key))
        self._ensure_storage_dir()
        self.files = self._load_index()
    
    def _derive_fernet_key(self, key: bytes) -> bytes:
        """Convert HMAC key to Fernet-compatible key"""
        import base64
        import hashlib
        return base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
    
    def _load_index(self) -> dict:
        """Load file index"""
        if os.path.exists(STORAGE_INDEX):
            with open(STORAGE_INDEX, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save file index"""
        with open(STORAGE_INDEX, 'w') as f:
            json.dump(self.files, f, indent=2)
    
    def add_file(self, file_path: str, display_name: Optional[str] = None) -> bool:
        """Encrypt and store a file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.cipher.encrypt(data)
            
            name = display_name or os.path.basename(file_path)
            file_id = f"{len(self.files)}_{name}"
            encrypted_path = os.path.join(STORAGE_DIR, f"{file_id}.enc")
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted)
            
            self.files[file_id] = {
                'name': name,
                'size': len(data),
                'encrypted_path': encrypted_path
            }
            self._save_index()
            return True
        except Exception:
            return False
    
    def get_file(self, file_id: str) -> Optional[bytes]:
        """Decrypt and retrieve a file"""
        try:
            if file_id not in self.files:
                print(f"[SecureStorage] file_id not found: {file_id}")
                return None
            
            encrypted_path = self.files[file_id]['encrypted_path']
            print(f"[SecureStorage] decrypting: {encrypted_path}")
            with open(encrypted_path, 'rb') as f:
                encrypted = f.read()
            
            return self.cipher.decrypt(encrypted)
        except Exception as e:
            print(f"[SecureStorage] decryption failed: {e}")
            return None
    
    def list_files(self) -> list:
        """List all stored files"""
        return [{'id': fid, **info} for fid, info in self.files.items()]
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a stored file"""
        try:
            if file_id not in self.files:
                return False
            
            encrypted_path = self.files[file_id]['encrypted_path']
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
            
            del self.files[file_id]
            self._save_index()
            return True
        except Exception:
            return False
