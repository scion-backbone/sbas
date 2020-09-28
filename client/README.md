# SBAS Customer

## Installation

Download and install [Wireguard](https://www.wireguard.com/install) on your system.
*Note:* on some distributions, the `resolvconf` package may also be required for `wg-quick`.

## Usage

Install the configuration for a node:
```
$ sudo ./install.sh [node] [ip]
```
where `[node]` is the node identifier (e.g., `oregon` or `frankfurt`), and `[ip]` sets an IP to assign to the customer's VPN endpoint.
This IP should be chosen from the `ext-prefix` range of the node that is connected to.

Once the configuration is installed, the VPN tunnel can be started and stopped using the following commands:
```
$ sudo ./start.sh [node]
$ sudo ./stop.sh [node]
```

