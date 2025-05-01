#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface

from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext

from mcdreforged.minecraft.rtext.text import RText
from mcdreforged.minecraft.rtext.style import RColor

from ..encrypt.exchange import publicToHash
from .. import shared


def printKey(source: CommandSource, ctx: CommandContext):
    if not source.get_permission_level() >= shared.config.commandPermission:
        source.reply(RText("你没有足够的权限", RColor.red))
        return
    source.reply(RText("此服务器的RCON公钥哈希 (SHA256):", RColor.gold))
    if shared.public:
        hex = publicToHash(shared.public).hex()
        source.reply(RText("前16位 ", RColor.gray)+RText(hex[:32], RColor.aqua))
        source.reply(RText("后16位 ", RColor.gray)+RText(hex[32:], RColor.aqua))
        source.reply(RText("验证此值于客户端的公钥哈希是否相同，若不同则代表有中间人", RColor.green))
        print(hex)
    else:
        source.reply(RText("公钥未初始化", RColor.red))


def registerAllCommands(serverInstance: PluginServerInterface):
    serverInstance.register_help_message("!!RCONkey", "获取RCON加密公钥哈希用验证", shared.config.commandPermission)

    tree = Literal('!!RCONkey').runs(printKey)

    serverInstance.register_command(tree)
