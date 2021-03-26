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
