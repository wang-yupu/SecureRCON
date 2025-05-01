
> Translated by ChatGPT-4o

---

# SecureRCON

An MCDR plugin that encrypts your RCON access and extends RCON functionality.

## Why?

The vanilla RCON protocol transmits data in plain text (including the password and commands), so encrypting RCON is useful. With extended RCON functionality, you can execute MCDR commands and send chat messages.

## Encryption Method and Access Instructions

After installing this plugin, if any ports on your machine are exposed to the internet, please use a firewall (e.g., ufw / firewalled / iptables) to block access. Also, set a strong RCON password. This plugin will automatically read the RCON password and listen on a port (default is 25575). The protocol on this port is compatible with the original RCON, so if you're using a vanilla RCON client, you can still connect using a fixed strong password or a dynamic one.

### SecureMCRCON Python Package

> Run `pip install securemcrcon` to install, then use the `smcrcon` command  
> [Repo](https://github.com/wang-yupu/SecureMCRCON)  
> [PyPI](https://pypi.org/project/securemcrcon/)

A CLI client.

### MCRCON App

> Coming soon (second priority)

<!-- [GitHub](https://github.com/wang-yupu/)
This app will support Windows / macOS (Coming Soon) / Linux (Coming Soon) / Android. It allows encrypted RCON connections and is also a feature-rich graphical RCON client. -->