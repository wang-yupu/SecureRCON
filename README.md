
# SecureRCON

一个MCDR插件，加密你的RCON访问

## Why?

原版的RCON是明文传输的（包括密钥与内容），因此加密RCON是有用的。

## 加密方法和访问方法

安装此插件后，如果机器的任意端口都暴露到网络，请使用防火墙进行拦截(e.g. ufw / firewalled / iptables)，同时设定一个较强的RCON密码。本插件会自动读取RCON密码，并监听一个端口(默认25575)，此端口的协议兼容原始RCON，若依然使用原版RCON客户端，可以使用固定强密码或者动态密码。

### MCRCON App

[GitHub](https://github.com/wang-yupu/)
此应用支持Windows / macOS(Coming Soon) / Linux(Coming Soon) / Android，可以用此应用进行加密RCON连接，本身也是一个不错的RCON图形化客户端
