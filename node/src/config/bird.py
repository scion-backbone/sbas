from src.config import parser
from src.config import consts
import textwrap

kernel_table_number = 151

def setup():
    local = parser.get_local_node()
    remote_pops = parser.get_remote_nodes()
    all_clients = parser.get_clients()
    local_router_ip = local["secure-router-ip"]
    sbas_asn = parser.get_sbas_asn()
    
    # Import bird template configuration file
    bird_template = open("src/config/bird-template.conf", "r")
    template_text = bird_template.read()
    bird_template.close()
    
    # Specify to which kernel table to import routes
    template_text = template_text.replace("$KERNEL_TABLE_NUMBER", str(kernel_table_number))
    template_text = template_text.replace("$SECURE_ROUTER_IP", str(local["secure-router-ip"]))
    template_text = template_text.replace("$SECURE_SUBPREFIX", str(local["secure-subprefix"]))

    # Define iBGP sessions with other PoPs
    for name, node in remote_pops.items(): 
        remote_nodename = name
        local_asn = str(sbas_asn)
        remote_asn = str(sbas_asn)
        ibgp_session = f'''
        protocol bgp {remote_nodename}01 {{
            local {local_router_ip} as {local_asn};
            neighbor {node["secure-router-ip"]} as {remote_asn};
            ipv4 {{
                table bgpannounce;
                import all;
                export filter {{
                    if (!safe_export()) then {{reject;}}
                    accept;
                }};
            }};
        }}
        '''
        template_text = template_text + textwrap.dedent(ibgp_session)

    # Define eBGP sessions with connected customers
    connected_clients = local["connected-clients"]
    for client in connected_clients:
        client_info = all_clients.get(client)
        if client_info: 
            local_asn = str(sbas_asn)
            client_asn = str(client_info["as-number"])
            client_providers = client_info["providers"]

            for provider in client_providers:
                if provider["id"] == parser.get_local_id():
                    ebgp_session = f'''
                    protocol bgp {client}01 {{
                        local {local_router_ip} as {local_asn};
                        neighbor {provider["local"]} as {client_asn};
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

                    '''
                    template_text = template_text + textwrap.dedent(ebgp_session)
            
    # Write bird configuration file
    bird_config = open("/etc/bird/bird.conf", "w")
    #bird_config = open("/home/scionlab/sbas/node/src/config/bird.conf", "w")
    bird_config.write(template_text)
    bird_config.close()
    
  

