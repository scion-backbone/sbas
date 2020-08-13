# SBAS Prototype

This repository serves the configuration for SBAS nodes, dynamically generated
from a single config file.

## Overview

### Structure

Information about the nodes that make up the SBAS is stored in `nodes.json`.
From this information, all the configurations are generated as follows:

- When run on a target machine, the `SBAS_NODE` environment variable must be set
  to the local node identifier.
- `gen.py` creates some configuration files (for SSH, SIG rules, Docker
  environment variables) and stores them in the `gen` directory.
- `scripts/db.sh` provides a convenient interface for shell script to access the node
  information in `nodes.json`.
- The sub-directories `sig` and `docker` contain additional configuration
  scripts that set up the SIG and Docker-based components respectively.

The `doc` directory contains additional documentation, such as the different
interfaces and address ranges used within the SBAS.

### SSH access to nodes

On your local machine, the `gen.py` generates an `sshconfig` from the node
configuration that can be used to access the nodes.

To install it on your system, run:
```
python3 gen.py
cat gen/sshconfig >> ~/.ssh/config
```

## Node Installation

*Pre-requisite:* A running SCIONLab node with default configuration.

Initially, set the `SBAS_NODE` variable to the name of the local node (as given
in the `nodes.json` file). Then, simply run `./install.sh` to perform the setup.
The SBAS components will be started automatically.

## Usage

### Running a Node

Use the shell scripts in the root directory to start and stop the node.
`reload.sh` must be run for configuration changes to take effect.

### SBAS Customers

*To do*

