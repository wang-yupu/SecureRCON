from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os

data = b"a secret message"
aad = b"authenticated but unencrypted data"

key = b"1234567890123456"*2
chacha = ChaCha20Poly1305(key)
nonce = os.urandom(12)
ct = chacha.encrypt(nonce, data, aad)
chacha.decrypt(nonce, ct, aad)
print(ct, chacha.decrypt(nonce, ct, aad))
