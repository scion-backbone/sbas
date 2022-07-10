# SBAS Prototype

Main code repository for the SBAS node and customer software.
Check the `config` repository for centralized topology information.

Components
- `node`: implementation for SBAS points of presence
- `client`: implementation for SBAS customers


# USENIX 22 AEC Instructions

Joining the current production SBAS network is not feasable because 1) we are upgrading the infrastructre and making changes which may disrupt connectivity and 2) the existing SBAS nodes would have to be manually configured to know the IPs of the artifact evaluator's nodes (in order to establish a connection with them) which could potenitally deanaymize the artifact evaluators and would require manual syncronzation during the evaluation process (as the new nodes would have to be added to nodes.json and then updated at all the production nodes).

Instead, we have instrctuions below for creating an entierly separate SBAS network consisting of two reviewer nodes configured from out-of-the-box Ubuntu VMs that are connected over SCIONLab and running the SBAS node software. While the SBAS prototype discussed in our paper uses the PEERING Testbed for BGP connectivity, giving access to the PEERING testbed to artifact evalurators would violate their Acceptable Use Policy and the prefix space we used is being reused for our current production infrastructure. Thus, these steps create a non-BGP version of SBAS that can only be used to route between secure prefixes attached to the different PoPs. Thus, these SBAS PoPs will not provide global routing connectivity to non-participating destinations (the way the discussed prototype does) but they will route between different PoPs over SCIONLab for secure traffic to participating destinations.

There are three major steps: 1) Spinning up two VMs and installing and changing preliminary network settings 2) Joining SCIONLab with both VMs and 3) Installing and configuring the SBAS Node software.

## 1. VM Configuration

Running SBAS requires a minimum of two VMs to serve as PoPs. The SBAS node software will securly route packets between them over SCION lab. For these instructions we used two VMs each running Ubuntu 22.04 x64 with 2048 MB RAM and 1 virtual CPU. Installation on other Ubuntu versions or other Debian systems should be similar, but this is the exact configuration used to generate these instructions.

Additionally, we had a root login on both VMs, so none of the commands in these instructions are prefixed with sudo. If you have a regular login, either elevate with `sudo -i` or add sudo where needed.

We recommend that you disable the firewall on the servers to prevent it from interfering with any of the networking. This is experimental software and it should not be run on any high-security systems. On Ubuntu run:

```
ufw disable
```

Also, enable IPv4 and IPv6 fowrading editing ```/etc/sysctl.conf``` and uncommenting the lines:
```
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
```

Run ```sysctl -p``` for the changes to take effect on the current boot.

## 2. Joining SCIONLab



