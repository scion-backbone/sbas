# SBAS Node

## Installation

*Pre-requisite:* A running SCIONLab node with default configuration.

**Note:** Currently, it is necessary to add an entry for the SIG to the `topology.json` file manually (on infrastructure nodes):
```
  ...
  "sigs": {
    "sig-1": {
      "ctrl_addr": "{INFRA_IP}:30256",
      "data_addr": "{INFRA_IP}:30056"
    }
  },
  ...
```
*The SCIONLab coordinator may occasionally attempt update this topology file, but will create a `.confnew` file instead of overwriting it.*

Initially, set the `SBAS_NODE` variable to the name of the local node (as given
in the `nodes.json` file). Then, simply run `./install.sh` to perform the setup.
The SBAS components will be started automatically.

## Usage

The `install.sh` script configures the system such that the SBAS node is started automatically with the system (`sbas.service` unit in `systemd`).

Use the `reload.sh` script for configuration changes to take effect.
