# SBAS Prototype

## Overview

This repository serves the configuration for SBAS nodes.
It is dynamically generated from the information in `nodes.json`.

Run `python3 gen.py` to create the configuration files, with argument `-n {node}` to generate node-specific files.

## SSH Access

The generated file `sshconfig` contains configuration to access the nodes.
To install, run:
```
cat sshconfig >> ~/.ssh/config
```

