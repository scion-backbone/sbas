from src.config import parser
from src.config import consts
import textwrap

kernel_table_number = 151

def setup():
    local = parser.get_local_node()
    remote_pops = parser.get_remote_nodes()
    all_clients = parser.get_clients()

    # Import bird template configuration file
    bird_template = open("src/config/bird-template.conf", "r")
    template_text = bird_template.read()
    bird_template.close()
    
    # Specify to which kernel table to import routes
    template_text = template_text.replace("$KERNEL_TABLE_NUMBER", str(kernel_table_number))
    template_text = template_text.replace("$EXTERNAL_PREFIX", str(local["ext-prefix"]))

    # Define iBGP sessions with other PoPs
    for name, node in remote_pops.items(): 
        remote_nodename = name
        local_asn = consts.SBAS_ASN 
        remote_asn = consts.SBAS_ASN
        ibgp_session = f'''
        protocol bgp {remote_nodename}01 {{
            local as {local_asn};
            neighbor {node["ext-vpn-ip"]} as {remote_asn};
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

    # Define eBGP sessions with connected Opt-In customers
    connected_clients = local["connected_clients"]
    for client in connected_clients:
        client_info = all_clients.get(client)
        if client_info: 
            local_asn = consts.SBAS_ASN
            client_asn = client_info["as_number"]
            client_providers = client_info["providers"]

            for provider in client_providers:
                if provider["id"] == parser.get_local_id():
                    ebgp_session = f'''
                    protocol bgp {client}01 {{
                        local as {local_asn};
                        neighbor {provider["local"]} as {client_asn};
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
                    template_text = template_text + textwrap.dedent(ebgp_session)
            
    """
    for name, node in all_clients.items():
        client_providers = node["providers"]
        
        for provider in client_providers:
            if provider["id"] == parser.get_local_id():
                client_nodename = name
                local_asn = consts.SBAS_ASN
                client_asn = node["as_number"] #65430 #must be read from updated client file
                ibgp_session = f'''
                protocol bgp {client_nodename}01 {{
                    local as {str(local_asn)};
                    neighbor {provider["local"]} as {str(client_asn)};
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
                template_text = template_text + textwrap.dedent(ebgp_session)


    """

    # Write bird configuration file
    bird_config = open("/etc/bird/bird.conf", "w")
    #bird_config = open("/home/scionlab/sbas/node/src/config/bird.conf", "w")
    bird_config.write(template_text)
    bird_config.close()
    
  

