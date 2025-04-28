#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.api.decorator.new_thread import new_thread
from .server import startServer
from . import shared
from .utils.backendContext import readFromServerProperties
import os.path


def on_load(server: PluginServerInterface, _):
    server.logger.info(
        f"SecureRCON v{server.get_plugin_metadata('securercon').version} was loaded")  # type: ignore

    shared.rcon = readFromServerProperties(os.path.dirname(os.path.dirname(server.get_data_folder())))

    server.logger.info(f"Starting RCON Server threading...")
    startServerOnNewThread()  # type: ignore


def on_unload(server: PluginServerInterface):
    server.logger.info("Stopping RCON Listener...")
    shared.stop = True
    while not shared.stopped:
        pass


@new_thread('SecureRCON')
def startServerOnNewThread():
    startServer()
