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

Run ```sysctl -p``` for the changes to take effect on the current boot. To differentiate the two servers, we will referr to one of them as node 1 and the other as node 2 even though both VMs have the same initial parameters.

Finally, we ran our VMs in the cloud provider Vultr (https://www.vultr.com/) which has low end options and a very simple default network configruation (no network firewall and no NAT). Other cloud providers should be similar, but care should be taken if they place VMs behind NAT or a network-level firewall enabled by default (which will not be disabled with ```ufw disable```) 

## 2. Joining SCIONLab

Visit https://www.scionlab.org/ and click Join SCIONLab in blue. Complete the signup form and the CAPTCHA. Check the provided email for the verification email to complete the account setup and then log in.

Once logged in with your SCIONLab account, click the blue button on your dashboard that reads "Create a new SCIONLab AS".

In label at the top, give the AS a name that corresponds to which node it is for. We will use "aec-1". Note that this label is arbitrary, but later on the node ids in the nodes.json file HAVE A LENGTH CONSTRAINT OF 10 CHARACTERS. For consistency, we use the same labels here as in the file, so we recommend choosing a short node name.

Select "SCION installation from packages". Scroll down to the section labeled Provider link. Using the drop-down for "Attachment point" select "18-ffaa:0:1206 (CMU AP)" This attachment point is currently active and we have had issues with other attachment points so we recommend this one. Next, put the **public IP address** of node 1. If you have an AWS EC2 node, please be mindful that they are given private IPs and the public IPs can be retrieved from the management console. Additionally, on EC2 (or any other node behind NAT), click "shown binding options for NAT" and enter the local private IP of the Internet interface in Bind IP address. Finally, EC2 and some cloud have a network firewall, so take care that the UDP port for SCIONLab (default 50000) is permitted through the firewall.

Finally, click "Create AS"

Repeat these steps to create a second AS and use the IP addresses of node 2 and set the label to correspond to node 2 (e.g., "aec-2"). Use the same attachment point and settings.


