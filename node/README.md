# SBAS Node

## Overview

- When run on a target machine, the `SBAS_NODE` environment variable must be set
  to the local node identifier.
- `scripts/gen.py` creates some configuration files (for SSH, SIG rules, Docker
  environment variables) and stores them in the `gen` directory.
- `scripts/db.sh` provides a convenient interface for shell script to access the node
  information in `nodes.json`.
- The sub-directories `sig` and `docker` contain additional configuration
  scripts that set up the SIG and Docker-based components respectively.

The `doc` directory contains additional documentation, such as the different
interfaces and address ranges used within the SBAS.

## SSH access to nodes

On your local machine, the `gen.py` generates an `sshconfig` from the node
configuration that can be used to access the nodes.

To install it on your system, run:
```
python3 scripts/gen.py
cat gen/sshconfig >> ~/.ssh/config
```

## Installation

*Pre-requisite:* A running SCIONLab node with default configuration.

Initially, set the `SBAS_NODE` variable to the name of the local node (as given
in the `nodes.json` file). Then, simply run `./install.sh` to perform the setup.
The SBAS components will be started automatically.

## Usage

Use the shell scripts in the root directory to start and stop the node.
`reload.sh` must be run for configuration changes to take effect.

