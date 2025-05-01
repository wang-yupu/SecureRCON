#
from dataclasses import dataclass
import javaproperties
import os


@dataclass
class RCONConnectionConfig:
    host: str
    port: int
    password: str


def readFromServerProperties(MCDRRoot: str, MCDRConfig: dict) -> RCONConnectionConfig:
    from ..shared import config
    fileContent = {}
    with open(os.path.join(MCDRRoot, MCDRConfig.get('working_directory', 'server'), 'server.properties')) as file:
        fileContent = javaproperties.loads(file.read())
    if config.backend.override:
        host = config.backend.host
        port = int(config.backend.port)
        password = str(config.backend.port)
    else:
        host = '127.0.0.1'
        port = int(fileContent.get('rcon.port', 25575))
        password = fileContent.get('rcon.password', '123456')

    return RCONConnectionConfig(host, port, password)
