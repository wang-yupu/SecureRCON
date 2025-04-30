
# 安全版本RCON 协议标准

## 前言

[Valve的RCON协议](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol)

## 扩展过的客户端请求

### 加密开始

> Type: `255`

服务端收到此数据包后开始密钥交换，密钥交换完后的所有内容都以加密传输

### Ping

> Type: `128`

服务端收到此数据包后返回一个同ID、同Type的数据包，Payload也一样

### MCDR指令

> Type: `8`

和普通的执行指令没有区别，只是用MCDR的指令系统解析（可能因服务端实现而异）

### Chat Start

> Type: `16`

将当前连接转换为聊天连接

### Chat End

> Type: `17`

回到命令连接

### Chat content

> Type: `20`

发送一段聊天信息。ID固定为-500

## 扩展过的服务端响应

### 加密握手回报

> Type: `255`

### Pong

> Type: `128`

见上文

### 聊天信息

> Type: `20`

服务端主动发送，代表一个聊天信息

### Chat Started

> Type: `16`

将当前连接转换为聊天连接

### Chat Ended

> Type: `17`

回到命令连接
