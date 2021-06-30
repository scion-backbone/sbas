from src.config import parser
from src.config import consts
from ipaddress import IPv4Network
import os, os.path
import textwrap
import subprocess

KERNEL_TABLE_NUMBER = 151
BIRD_TABLE_NAME = 'bgpannounce'

def setup():
    local = parser.get_local_node()
    remote_pops = parser.get_remote_nodes()
    all_clients = parser.get_clients()
    local_router_ip = local['secure-router-ip']
    sbas_asn = parser.get_sbas_asn()
    sbas_prefix = parser.get_sbas_prefix()
    
    # Prepare custom announcements for SBAS prefix
    try:
        # Create directory to store configuration for custom announcements
        os.makedirs(os.path.join(consts.ETC_BIRD, consts.BIRD_ROUTE_ANNOUNCEMENTS_DIR), exist_ok=True)
    except e:
        print('Error while creating route-announcements directory' + e)
        exit(1)

    sbas_network = IPv4Network(sbas_prefix)
    secure_prefix_filter_list = ', '.join([str(subnet) for subnet in sbas_network.subnets()])
    
    # Advertise the two subnetworks of the secure SBAS prefix and create the necessary files 
    for subnet in sbas_network.subnets():
        route_announcement_content = f"route {subnet} unreachable;"
        with open(os.path.join(consts.ETC_BIRD, consts.BIRD_ROUTE_ANNOUNCEMENTS_DIR, str(subnet).replace('/', "-")), "w") as f:
            f.write(route_announcement_content)  

    # Import bird template configuration file
    content = ""
    with open("src/config/bird-template.conf", "r") as f:
        content = f.read()
    
    # Substitute variables in template
    for k, v in {
        'KERNEL_TABLE_NUMBER': KERNEL_TABLE_NUMBER,
        'BIRD_TABLE_NAME': BIRD_TABLE_NAME,
        'SECURE_ROUTER_IP': local['secure-router-ip'],
        'SECURE_SUBPREFIX': local['secure-subprefix'],
        'SECURE_PREFIX_LIST': secure_prefix_filter_list,
        'SBAS_ASN': sbas_asn 
    }.items():
        content = content.replace(f"${k}", str(v))

    #Initialize the configuration of the static protocol
    static_protocol = textwrap.dedent(f'''
        protocol static {{
            ipv4 {{
                table {BIRD_TABLE_NAME};
            }};
            include "route-announcements/*";
        ''')

    for name, node in remote_pops.items(): 
        remote_nodename = name
        remote_asn = sbas_asn
        remote_subprefix = node['secure-subprefix']
        
        # Add static routes in the static protocol for each subprefix of the other PoPs
        # In multihop BGP sessions, BIRD cannot resolve the next hop and shows the learnt prefixes as unreachable.
        # To resolve this issue, we need to explicitly specify routes to the next hops. Adding static routes for the 
        # subprefixes of the PoPs resolves this issue.
        static_route = f'    route {remote_subprefix} via {local_router_ip};\n'
        static_protocol += static_route
        
        # Define iBGP sessions with other PoPs
        ibgp_session = textwrap.dedent(f'''
        protocol bgp {remote_nodename}01 from iBGP_pop {{
            neighbor {node['secure-router-ip']} as {remote_asn}; 
        }}

        ''')
        content += ibgp_session
    
    # End configuration of static protocol
    static_protocol += '}' 

    # Define eBGP sessions with connected customers
    connected_clients = local['connected-clients']
    for client in connected_clients:
        client_info = all_clients.get(client)
        if client_info: 
            client_asn =  client_info['as-number']
            client_providers = client_info['providers']

            for provider in client_providers:
                if provider['id'] == parser.get_local_id():
                    ebgp_session = textwrap.dedent(f'''
                    protocol bgp {client}01 from eBGP_client {{
                        neighbor {provider['local']} as {client_asn};
                        ipv4 {{
                            import filter {{
                                if (!safe_import_from_clients({client_asn})) then {{reject;}}
                                accept;
                            }};
                        }};
                    }} 

                    ''')
                    content += ebgp_session

    content += static_protocol # Append configuration for static protocol

    # Write bird configuration file
    with open(os.path.join(consts.ETC_BIRD, consts.BIRD_CONF), "w") as f:
        f.write(content)

def start():
    subprocess.run(["sudo", "systemctl", "start", "bird"],
            stdout=subprocess.PIPE, # capture stdout
            stderr=subprocess.PIPE # capture stderr
    )

def stop():
    subprocess.run(["sudo", "systemctl", "stop", "bird"],
            stdout=subprocess.PIPE, # capture stdout
            stderr=subprocess.PIPE # capture stderr
    )