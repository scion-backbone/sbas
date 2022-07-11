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

Repeat these steps to create a second AS and use the IP addresses of node 2 and set the label to correspond to node 2 (e.g., "aec-2"). Use the same attachment point and settings (but make sure to update the public IP to that of node 2).

With both ASes created, go to "My ASes" (upper left) and click the AS for node 1. Be sure "SCION installation from packages" is selected and run the commands for the Ubuntu package install on node 1. For reference, they are:

```
sudo apt-get install apt-transport-https ca-certificates
echo "deb [trusted=yes] https://packages.netsec.inf.ethz.ch/debian all main" | sudo tee /etc/apt/sources.list.d/scionlab.list
sudo apt-get update
sudo apt-get install scionlab
```

Then, configure the SCIONLab AS with:
```
sudo scionlab-config --host-id=<...> --host-secret=<...>
```
If you have already created your AS (as instructed in this document), the host id and host secret will be filled in on the webpage with the values specific to your SCIONLab AS.

Repeat these instructions for node 2 and be sure to use the host id and host secret specific to node 2.

On node 1 and node 2, run ```sudo systemctl start scionlab.target``` to start all SCION services.

At this point, both node 1 and node 2 should be connected to SCIONLab.

To test the configuration, check the status of the SCIONLab services:
```
sudo systemctl list-dependencies scionlab.target
```
All services running implies a successful configuration.

Finally, install the SCION apps with:
```
sudo apt install scion-apps-*
```

You can also perform a bandwidth test with a public SCION bandwidth server with ```scion-bwtestclient -s 16-ffaa:0:1001,[172.31.0.23]:30100```
Results of a successful bandwidth test look like:
```
root@usenix-aec-node-2:~# scion-bwtestclient -s 16-ffaa:0:1001,[172.31.0.23]:30100

Test parameters:
client->server: 3 seconds, 1000 bytes, 30 packets
server->client: 3 seconds, 1000 bytes, 30 packets
We need to sleep for 1 seconds before we can get the results

S->C results
Attempted bandwidth: 80000 bps / 0.08 Mbps
Achieved bandwidth: 80000 bps / 0.08 Mbps
Loss rate: 0.0%
Interarrival time min/avg/max/mdev = 101.732/103.484/105.193/1.307 ms

C->S results
Attempted bandwidth: 80000 bps / 0.08 Mbps
Achieved bandwidth: 80000 bps / 0.08 Mbps
Loss rate: 0.0%
Interarrival time min/avg/max/mdev = 101.236/103.484/105.831/1.532 ms
root@usenix-aec-node-2:~#
```

A list of alternate public servers can be found at https://docs.scionlab.org/content/apps/bwtester.html


Additional documentation to configure SCIONLab can be found at https://docs.scionlab.org/content/install/pkg.html 

## 3. Installing SBAS

On both node 1 and node 2, clone the SBAS repository (i.e., this repo) with:

```
git clone https://github.com/scion-backbone/sbas.git
```

CD to the node directory of the repo with ```cd sbas/node```

Install dependencies with ```./deps``` (note that with the SCION repositories added to APT from the SCIONLab installation, scion-sig should be found correctly)

Run ```./configure``` and specify a distinct node ID on each node. THIS NODE ID MUST BE UNDER 10 CHARS. We will use aec-1 and aec-2 in thid document. Unlike the labels on the SCIONLab ASes, these node ids must be consistant throughout the remainder of these instructions as this node ID will reference which config values that node will use.

At this point, DO NOT RUN MAKE INSTALL. ```./configure``` downloaded a default configuraiton from our public repo, this will not work for your specific configuration as you are not connecting to the main SBAS deployment. The primary file that needs to be updated is ```build/nodes.json``` (note that this is relative to the ```sbas/node``` directory).

Below is a template config file that you can use as a starting point, but many of the values need to be updated for your specific install per the instructions below. Also, both nodes use the same nodes.json file so this template only needs to be filled out once with information about both nodes and then each node will load the configs specified under to that node's node id.

```
{
   "secure-prefix":"10.22.0.0/23",
   "as-number":65432,
   "nodes":{
      "aec-1":{
         "public-ip":"140.82.18.98",
         "scion-ia":"18-ffaa:1:fd6",
         "internal-prefix":"172.22.1.0/24",
         "internal-ip":"172.22.1.1",
         "secure-subprefix":"10.22.0.0/24",
         "secure-vpn-ip":"10.22.0.1",
         "secure-router-ip":"10.22.0.2",
         "global-gateway":"local",
         "internet-ip-gateway":"207.148.24.1",
         "vpn-public-key":"67l11hqm6cNkFQo1CyaLjpeuUo8SyqoT0I42Olt/N30=",
         "connected-clients":[
            
         ]
      },
      "aec-2":{
         "public-ip":"140.82.18.98",
         "scion-ia":"20-ffaa:1:fd7",
         "internal-prefix":"172.22.2.0/24",
         "internal-ip":"172.22.2.1",
         "secure-subprefix":"10.22.1.0/24",
         "secure-vpn-ip":"10.22.1.1",
         "secure-router-ip":"10.22.1.2",
         "global-gateway":"local",
         "internet-ip-gateway":"140.82.18.1",
         "vpn-public-key":"67l11hqm6cNkFQo1CyaLjpeuUo8SyqoT0I42Olt/N30=",
         "connected-clients":[
            
         ]
      }
   }
}
```

To explain the values in detail. Values prefixed with MUST BE UPDATED must be updated to reflect the invoronment of that specific install. The others can be left as is.

```secure-prefix``` in the root of the JSON file specifies the overarching IP range used for all secure communication within SBAS. In our SBAS prototype this was also announced with BGP for reachability with non-participating destinations, but since this install is not connected to BGP, this can be any private IP range (or even a public range so long as it is not an IP used on the LAN of one of the nodes; secure routes are always prefered over Internet routes so the system is still fully funcitonal if this prefix is announced publically by a third party, as in a BGP hijack). While any IP range can be used, the ```10.22.0.0/23``` from this example can simply be reused.

```as-number``` in the root of the JSON file specifies the AS number for SBAS operations. The private ASN 65432 can simply be reused.

MIGHT NEED TO BE UPDATED (depending on node name passed to ./configure) ```nodes``` contains info for all the nodes in this SBAS topology. The keys under nodes MUST MATCH the node name given to ```./configure```. We use aec-1 and aec-2 and reusinng these is fine.

Below are keys within the node object:
MUST BE UPDATED ```public-ip``` The public IP of that specific node. MUST BE UPDATED WITH THE TRUE PUBLIC IP of node 1 and node 2

MUST BE UPDATED ```scion-ia``` This is the SCIONLab AS of node 1 and node 2. This value must be accurate or the scion-ip-gateways (or SIGs) that SBAS nodes use will not be able to connect to each other. To get the full SCIONLab AS for each node goto the My ASes page (https://www.scionlab.org/user/) when logged into your SCIONLab account. DO NOT CLICK THE ASes, read the "AS ID" corresponding to node 1 and node 2 from this page and put them into the nodes.json file. If you click on an AS and use that to get the AS ID, it will give a truncated version at the top of the page which will not work. The full AS ID should contain a hyphen before the first colon (like "18-ffaa:1:fd6" not just "ffaa:1:fd6").


```internal-prefix``` This is a prefix used by this SBAS node for GRE tunnels. It should be private and does not need to be changed. It is different from the secure prefix which is used for connecting customers and the routing control plane.

```internal-ip``` An IP in the internal prefix for GRE tunnels.

```secure-subprefix``` A subprefix of ```secure-prefix``` used for customers of that sepcfici node.

```secure-vpn-ip``` The VPN IP on the secure prefix

```secure-router-ip``` The router IP on the secure prefix

```global-gateway``` Says that this node can be used for outbound Internet traffic. Even though BGP is not configured, leave it for syntactic reasons.

MUST BE UPDATED ```internet-ip-gateway``` This is the IP of the next hop on the default route. Although routing configurations may vary, this can usually be found by running ```ip route``` on the node and finding the IP address on the default route (i.e., the line that starts with ```default``` or ```0.0.0.0/0```) after ```via```. In the following routing output:
```
default via 207.148.24.1 dev enp1s0 proto dhcp src 207.148.24.134 metric 100 
108.61.10.10 via 207.148.24.1 dev enp1s0 proto dhcp src 207.148.24.134 metric 100 
169.254.169.254 via 207.148.24.1 dev enp1s0 proto dhcp src 207.148.24.134 metric 100 
207.148.24.0/23 dev enp1s0 proto kernel scope link src 207.148.24.134 metric 100 
207.148.24.1 dev enp1s0 proto dhcp scope link src 207.148.24.134 metric 100
```
"207.148.24.1" is the ```internet-ip-gateway```

```vpn-public-key``` is the public IP of the wireguard VPN. This can be updated manually after the configuration if clients need to be connected.

```connected-clients``` leave this as an empty list. Clients can be connected manually later.

With all these updates in place to ```nodes.json```, uplaod it to both 

Before running make install, edit the file ```src/config/consts.py``` (once again relative to the ```sbas/node``` directory). Add the following line:
```
INTERNET_GATEWAY_IP = '<internet-ip-gateway>'
```
Where ```<internet-ip-gateway>``` is the ```internet-ip-gateway``` from above. So in our example that would be:
```
INTERNET_GATEWAY_IP = '207.148.24.1'
```
Make sure the IP is encapsulated in single quotes as shown.


With all the configuration changes in place, run ```make install```

Run ```service sbas start```

At this point, check the status of the SBAS service with ```service sbas status```. It should show it as active if all configurations were correct. If the service has failed, keep in mind that when the service startup fails, the cleanup commands also fail so the first error message is usually the root cause. Most SBAS service failures have to do with improper values in ```build/nodes.json``` or ```src/config/consts.py```. Restaring the SBAS service with ```service sbas stop``` and ```service sbas start``` can occationally help resolve problems with stale configs/routes. If any changes are made to ```build/nodes.json```, be sure to rerun ```make install``` to copy new config file to the ```etc/sbas``` directory.

Double check the status of the SIG with ```sudo systemctl status scion-ip-gateway.service```
Lines that start with ```Start prefix discovery``` indicate the sig is searching for the prefixes available by the other SIG. Issues with the SIG configuration often have to do with improper values of ```scion-ia```. The sig can be restarted after a config change (which will happen when ```make install``` is run again on the SBAS repo) with: ```sudo systemctl stop scion-ip-gateway.service``` and ```sudo systemctl start scion-ip-gateway.service```.

The SIG takes several seconds to connect and discover the other SIG, but an operational SIG will add a network device called ```sig``` which can be shown with ```ip a```.

If all services are functional, and the ```sig``` device is listed, connectivity should be established. The first test of connectivity is to test the infrastructure prefixes (handled by the SIG) with a ping. On node 1 run:

```ping 172.22.2.1```

To ping the infrastructure IP of node 2. If this is successful, the SIG configuraiton is operational and allowing for IPs to ping over SCION.

The next step to test connectivity is to ping from the secure VPN IPs. These IPs are in the secure prefix and routing is the same for them as it is for SBAS customers that connect to these PoPs. To run this ping run:

```ping -I 10.22.0.1 10.22.1.1```

This makes the source address the local secure VPN IP (required for proper reverse routing) and pings the remote secure VPN IP of node 2, If this ping is successful, the two SBAS nodes are communicating over SCIONLab and securly routing customer SBAS traffic.


