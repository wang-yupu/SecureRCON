#
from dataclasses import dataclass
import configparser


@dataclass
class RCONConnectionConfig:
    host: str
    port: int
    password: str


def readFromServerProperties(MCDRRoot: str) -> RCONConnectionConfig:
    host = "127.0.0.1"
    port = 25575
    password = "123456"
    return RCONConnectionConfig(host, port, password)
