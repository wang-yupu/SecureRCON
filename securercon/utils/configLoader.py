from pydantic import BaseModel
import yaml
from pathlib import Path


class NetworkConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 25576
    maxConnection: int = 5
    timeout: float = 2.5
    bufsize: int = 2048


class FixedPasswordConfig(BaseModel):
    enable: bool = True
    password: str = ""
    requireEncrypt: bool = False


class DynmaicPasswordConfig(BaseModel):
    enable: bool = True
    key: str = ""
    length: int = 18
    requireEncrypt: bool = False


class AuthorizationConfig(BaseModel):
    fixed: FixedPasswordConfig = FixedPasswordConfig()
    dynmaic: DynmaicPasswordConfig = DynmaicPasswordConfig()
    enableEncrypt: bool = True


class BackendConfig(BaseModel):
    override: bool = False
    password: str = ''
    port: int = 25575
    host: str = '127.0.0.1'


class Config(BaseModel):
    network: NetworkConfig = NetworkConfig()
    authorization: AuthorizationConfig = AuthorizationConfig()
    backend: BackendConfig = BackendConfig()


def loadConfig(filename: str) -> Config:
    configPath = Path(filename)

    rawConfig = {}
    if configPath.exists():
        with configPath.open("r", encoding="utf-8") as file:
            rawConfig = yaml.safe_load(file) or {}
    else:
        with open(configPath, "w", encoding="utf-8") as file:
            yaml.dump(Config().model_dump(), file, sort_keys=False, allow_unicode=True)

    config = Config(**rawConfig)
    fullDict = config.model_dump()
    if fullDict != rawConfig:
        with configPath.open("w", encoding="utf-8") as file:
            yaml.dump(fullDict, file, sort_keys=False, allow_unicode=True)

    return config
