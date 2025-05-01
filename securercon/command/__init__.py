#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface

from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext


def printKey(source: CommandSource, ctx: CommandContext):
    ...


def registerAllCommands(serverInstance: PluginServerInterface):
    serverInstance.register_help_message("!!RCONkey", "获取RCON加密公钥哈希用验证", config.cfg.get("cfgCmdPermission", 4))

    tree = Literal('!!RCONkey').runs(printKey)

    serverInstance.register_command(tree)
