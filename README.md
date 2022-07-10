# SBAS Prototype

Main code repository for the SBAS node and customer software.
Check the `config` repository for centralized topology information.

Components
- `node`: implementation for SBAS points of presence
- `client`: implementation for SBAS customers


# USENIX 22 AEC Instructions

Joining the current production SBAS network is not feasable because 1) we are upgrading the infrastructre and making changes which may disrupt connectivity and 2) the existing SBAS nodes would have to be manually configured to know the IPs of the artifact evaluator's nodes (in order to establish a connection with them) which could potenitally deanaymize the artifact evaluators and would require manual syncronzation during the evaluation process (as the new nodes would have to be added to nodes.json and then updated at all the production nodes).

Instead, we have instrctuions below for creating an entierly separate SBAS network consisting of two reviewer nodes configured from out-of-the-box Ubuntu VMs that are connected over SCIONLab and running the SBAS node software. While the SBAS prototype discussed in our paper uses the PEERING Testbed for BGP connectivity, giving access to the PEERING testbed to artifact evalurators would violate their Acceptable Use Policy and the prefix space we used is being reused for our current production infrastructure. Thus, these steps create a non-BGP version of SBAS that can only be used to route between secure prefixes attached to the different PoPs. Thus, these SBAS PoPs will not provide global routing connectivity to non-participating destinations (the way the discussed prototype does) but they will route between different PoPs over SCIONLab for secure traffic to participating destinations.
