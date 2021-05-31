# SBAS Node

## Installation

*Pre-requisite:* A running SCIONLab node with default configuration.
Check the `config` repository for ssh access configuration.

1. `./configure` to check for dependencies and create configuration files
   (on Debian-based systems, dependencies can be created automatically using `./deps`)
2. `sudo make install` to install

The installation script creates configuration at `/etc/sbas` and stores all static assets at `/lib/sbas`.
An executable is linked to `/usr/bin/sbas`, but in most cases, the user will not need to interface with it.
Instead, the `systemd` service `sbas` will be used.

Run `sudo systemctl status sbas` to check the status of the service and `sudo journalctl -u sbas` to check its logs.

## Development

To apply changes, it is sufficient to re-run `sudo make install`.
On topology changes (`config`), the new configuration also needs to be fetched, e.g., by running `./configure` first.
The `systemd` service will be restarted automatically if it was previously running.

## Components

- Docker container: inside a single container, we currently run the gateways to
  customers and the Internet.
  - WireGuard
  - BIRD router
- SCION-IP gateway: installed via the normal SCION packages, runs as a `systemd`
  service (which is a dependency of the SBAS service)
- Routing logic: runs directly on the SCIONLab machine OS

## Debugging

Output from the main thread is captured by `systemd` and can be viewed using `journalctl`:
```
sudo journalctl -u sbas
```

The SCION-IP gateway runs as its own `systemd` service that also collects logs:
```
sudo journalctl -u scion-ip-gateway
```

It is often useful to access the Docker container for further debugging.
To run a shell on it, run this command:
```
sudo docker exec -it docker_vpn_router_1 bash
```
