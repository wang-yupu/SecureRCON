# from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
# import os

# data = b"a secret message"
# aad = b"authenticated but unencrypted data"

# key = b"1234567890123456"*2
# chacha = ChaCha20Poly1305(key)
# nonce = os.urandom(12)
# ct = chacha.encrypt(nonce, data, aad)
# chacha.decrypt(nonce, ct, aad)
# print(ct, chacha.decrypt(nonce, ct, aad))


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
# Generate a private key for use in the exchange.
private_key = X25519PrivateKey.generate()
peer_public_key = X25519PrivateKey.generate().public_key()
shared_key = private_key.exchange(peer_public_key)
# Perform key derivation.
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'handshake data',
).derive(shared_key)

# # For the next handshake we MUST generate another private key.
# private_key_2 = X25519PrivateKey.generate()
# peer_public_key_2 = X25519PrivateKey.generate().public_key()
# shared_key_2 = private_key_2.exchange(peer_public_key_2)
# derived_key_2 = HKDF(
#     algorithm=hashes.SHA256(),
#     length=32,
#     salt=None,
#     info=b'handshake data',
# ).derive(shared_key_2)
