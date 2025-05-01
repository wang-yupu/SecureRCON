from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import hashlib


def ChaCha20Poly1305Encrypt(data: bytes, key: bytes, aad: bytes | None = None, seq: int = 0) -> bytes:
    chacha = ChaCha20Poly1305(key)
    nonce = hashlib.sha256(str(seq).encode(encoding='utf-8')).digest()[:12]
    return chacha.encrypt(nonce, data, aad)


def ChaCha20Poly1305Decrypt(data: bytes, key: bytes, aad: bytes | None = None, seq: int = 0) -> bytes:
    chacha = ChaCha20Poly1305(key)
    nonce = hashlib.sha256(str(seq).encode(encoding='utf-8')).digest()[:12]
    return chacha.decrypt(nonce, data, aad)
