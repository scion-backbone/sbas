from src.config import parser
from src.config import consts
import textwrap

kernel_table_number = 151

def setup():
    local = parser.get_local_node()
    remote_pops = parser.get_remote_nodes()

    # Import bird template configuration file
    bird_template = open("src/config/bird-template.conf", "r")
    template_text = bird_template.read()
    bird_template.close()
    
    # Specify to which kernel table to import routes
    template_text = template_text.replace("$KERNEL_TABLE_NUMBER", str(kernel_table_number))
    template_text = template_text.replace("$INTERNAL_PREFIX", str(local["int-prefix"]))

    # Define iBGP sessions with other PoPs
    for name, node in remote_pops.items(): 
        remote_nodename = name
        local_asn = 65432
        remote_asn = 65432
        bgp_session = f'''
        protocol bgp {remote_nodename}01 {{
            local as {str(local_asn)};
            neighbor {node["ext-vpn-ip"]} as {str(remote_asn)};
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
        template_text = template_text + textwrap.dedent(bgp_session)

    # Define eBGP sessions with connected Opt-In customers
    
    # Write bird configuration file
    bird_config = open("/home/scionlab/sbas/node/src/config/bird.conf", "w")
    bird_config.write(template_text)
    bird_config.close()
    
  

