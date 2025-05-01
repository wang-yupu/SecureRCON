#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.api.decorator.new_thread import new_thread
from mcdreforged.info_reactor.info import Info

from securercon.encrypt import exchange
from .server import startServer
from . import shared
from .utils.backendContext import readFromServerProperties
from .utils.configLoader import loadConfig
from .encrypt.exchange import loadKeyPair
import os.path


def on_load(server: PluginServerInterface, _):
    try:
        onLoad(server)
    except Exception as error:
        server.logger.error(f"Failed to execute on_load event. Error: {error}")
        shared.stopped = True


def onLoad(server: PluginServerInterface):
    server.logger.info(
        f"SecureRCON v{server.get_plugin_metadata('securercon').version} was loaded")  # type: ignore

    # 加载配置
    MCDRRoot = os.path.dirname(
        os.path.dirname(server.get_data_folder()))
    shared.rcon = readFromServerProperties(MCDRRoot, server.get_mcdr_config())
    shared.config = loadConfig(os.path.join(MCDRRoot, "config/securercon/config.yaml"))
    server.logger.info(
        f"Using RCON config: {shared.rcon.host}:{shared.rcon.port} with password: {shared.rcon.password[:2]}{(len(shared.rcon.password)-4)*'*'}{shared.rcon.password[-2:]}")
    shared.private, shared.public = loadKeyPair(server.get_data_folder())

    shared.private, shared.public = exchange.newKeyPair()
    server.logger.info(f"Starting RCON Server threading...")
    startServerOnNewThread(server)  # type: ignore


def on_unload(server: PluginServerInterface):
    server.logger.info("Stopping RCON Listener...")
    shared.stop = True
    while not shared.stopped:
        pass


def on_user_info(server: PluginServerInterface, info: Info):
    if info.is_player:
        for _, cb in shared.chatTriggers.items():
            try:
                cb(info.player, info.content)
            except:
                server.logger.warning("Failed to put something to chat queue.")


@new_thread('SecureRCON-TCPServer')
def startServerOnNewThread(server: PluginServerInterface):
    startServer(server.logger, server.broadcast)
    shared.stopped = True
