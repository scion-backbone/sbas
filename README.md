# SBAS Prototype

## Overview

This repository serves the configuration for SBAS nodes.
It is dynamically generated from the information in `nodes.json`.

Run `python3 gen.py` to create the configuration files.
To to generate node-specific files, set the variable `$SBAS_NODE`.

## SSH access

The generated file `sshconfig` contains configuration to access the nodes.
To install, run:
```
cat sshconfig >> ~/.ssh/config
```

## Setting up on a SCIONLab node

### SCION-IP Gateway (SIG)

On a SCIONLab node with a running SCION setup, first set the variable `$SBAS_NODE` to the local node name.
Then, run the following scripts in order to set up the SIG:

```
cd sig
./env.sh
./install.sh
./configure.sh
```

If changes are made to the SBAS configuration, it is sufficient to simply to re-run the `configure.sh` script.

### Other Components

The router (based on BIRD) and the VPN endpoint run in their respective Docker containers.

