from src.config import parser
from src.config import consts
import textwrap

KERNEL_TABLE_NUMBER = 151

def setup():
    local = parser.get_local_node()
    remote_pops = parser.get_remote_nodes()
    all_clients = parser.get_clients()
    local_router_ip = local['secure-router-ip']
    sbas_asn = parser.get_sbas_asn()
    
    # Import bird template configuration file
    content = ""
    with open("src/config/bird-template.conf", "r") as f:
        content = f.read()
    
    # Substitute variables in template
    for k, v in {
        'KERNEL_TABLE_NUMBER': KERNEL_TABLE_NUMBER,
        'SECURE_ROUTER_IP': local['secure-router-ip'],
        'SECURE_SUBPREFIX': local['secure-subprefix'],
    }.items():
        content = content.replace(f"${k}", str(v))

    # Define iBGP sessions with other PoPs
    for name, node in remote_pops.items(): 
        remote_nodename = name
        local_asn = sbas_asn
        remote_asn = sbas_asn
        ibgp_session = textwrap.dedent(f'''
        protocol bgp {remote_nodename}01 {{
            local {local_router_ip} as {local_asn};
            neighbor {node['secure-router-ip']} as {remote_asn};
            ipv4 {{
                table bgpannounce;
                import all;
                export filter {{
                    if (!safe_export()) then {{reject;}}
                    accept;
                }};
            }};
        }}
        ''')
        content += ibgp_session

    # Define eBGP sessions with connected customers
    connected_clients = local['connected-clients']
    for client in connected_clients:
        client_info = all_clients.get(client)
        if client_info: 
            local_asn = sbas_asn
            client_asn =  client_info['as-number']
            client_providers = client_info['providers']

            for provider in client_providers:
                if provider['id'] == parser.get_local_id():
                    ebgp_session = textwrap.dedent(f'''
                    protocol bgp {client}01 {{
                        local {local_router_ip} as {local_asn};
                        neighbor {provider['local']} as {client_asn};
                        ipv4 {{
                            table bgpannounce;
                            import all;
                            export filter {{
                                if (!safe_export()) then {{reject;}}
                                    accept;
                            }};
                        }};
                        multihop;
                    }}

                    ''')
                    content += ebgp_session
            
    # Write bird configuration file
    with open("/etc/bird/bird.conf", "w") as f:
        f.write(content)
