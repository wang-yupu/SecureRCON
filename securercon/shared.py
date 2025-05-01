#
from .utils.backendContext import RCONConnectionConfig
from cryptography.hazmat.primitives.asymmetric import x25519
from .utils.configLoader import Config

config: Config = Config()

stop: bool = False
stopped: bool = False

rcon: RCONConnectionConfig = RCONConnectionConfig('127.0.0.1', 25575, 'default')

public: x25519.X25519PublicKey | None = None
private: x25519.X25519PrivateKey | None = None

chatTriggers = {}
