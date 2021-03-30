# SBAS Node

## Installation

*Pre-requisite:* A running SCIONLab node with default configuration.
Check the `config` repository for ssh access configuration.

1. `./configure` to check for dependencies and create configuration files
2. `sudo make install` to install

The installation script creates configuration at `/etc/sbas` and stores all static assets at `/lib/sbas`.
An executable is linked to `/usr/bin/sbas`, but in most cases, the user will not need to interface with it.
Instead, the `systemd` service `sbas` will be used.

Run `sudo systemctl status sbas` to check the status of the service and `sudo journalctl -u sbas` to check its logs.

## Development

To apply changes, it is sufficient to re-run `sudo make install`.
The `systemd` service will be restarted automatically if it was previously running.

## Components

- Docker container
  - WireGuard
  - BIRD router
- SCION-IP gateway
- Routing logic
