#
from .utils.backendContext import RCONConnectionConfig
stop = False
stopped = False

rcon: RCONConnectionConfig = RCONConnectionConfig('127.0.0.1', 25575, 'default')
