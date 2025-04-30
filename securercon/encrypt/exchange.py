#
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization


def loadKeyPair(dirName: str) -> tuple[x25519.X25519PrivateKey, x25519.X25519PublicKey]:
    ...


def newKeyPair() -> tuple[x25519.X25519PrivateKey, x25519.X25519PublicKey]:
    private = x25519.X25519PrivateKey.generate()
    return private, private.public_key()


def toBase85(key: x25519.X25519PublicKey | x25519.X25519PrivateKey) -> str:
    if isinstance(key, x25519.X25519PrivateKey):
        return base64.b85encode(key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )).decode(encoding='utf-8')
    elif isinstance(key, x25519.X25519PublicKey):
        return base64.b85encode(key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )).decode(encoding='utf-8')
    else:
        raise TypeError("Not a public or private key!")


def toJSONString(privateKey: x25519.X25519PrivateKey, publicKey: x25519.X25519PublicKey) -> str:
    private = toBase85(privateKey)
    public = toBase85(publicKey)

    data = {
        "private": private,
        "public": public,
        "WARNING": "DO NOT MODIFY THIS FILE EXCEPT YOU KNOW WHAT ARE YOU DOING!",
        "WARNING2": "DO NOT SHARE THIS FILE EXCEPT YOU WANT TO TRY MITM",
        "WARNING_CN": "不要修改这个文件除非你知道你在干什么",
        "WARNING2_CN": "不要把这个文件发出去除非你真的想要试一下MITM等攻击"
    }

    return json.dumps(data, ensure_ascii=False)


def fromJSONString(data: str) -> tuple[x25519.X25519PrivateKey, x25519.X25519PublicKey] | None:
    try:
        obj = json.loads(data)

        privateBytes = base64.b85decode(obj["private"])
        publicBytes = base64.b85decode(obj["public"])

        privateKey = x25519.X25519PrivateKey.from_private_bytes(privateBytes)
        publicKey = x25519.X25519PublicKey.from_public_bytes(publicBytes)

        return privateKey, publicKey
    except:
        raise Exception("Failed to load keys.")


def exchange(private: x25519.X25519PrivateKey, peerPublic: x25519.X25519PublicKey, salt: bytes | None = None, info: bytes = b'INFO', length=32) -> bytes:
    sharedKey = private.exchange(peerPublic)
    key = HKDF(
        algorithm=hashes.SHA512(),
        length=length,
        salt=salt,
        info=info,
    ).derive(sharedKey)

    return key
