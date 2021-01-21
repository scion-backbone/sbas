# Experiments

The infrastructure is designed as follows:
A (local) machine serves as command-and-control and uses SSH connections to SBAS nodes and customers to orchestrate experiments
The directory `remote` contains helper scripts that run remotely, and the remaining code is designed to run on the local machine.

`sshconfig` contains client machines.

## Instructions

**[Deprecated]** How to run an experiment:

- Make sure the required SBAS nodes are running
- Navigate to the `client` directory in the repository root
- Install the prerequisites (WireGuard)
- Navigate to the experiment directory
- Use the experiment-specific scripts

