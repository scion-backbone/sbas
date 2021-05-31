from src.config import parser
from src.config import consts
import textwrap

kernel_table_number = 151

def setup():
    local = parser.get_config()
    all_pops = parser.get_nodes()
    providers = local["providers"]

    bird_template = open("src/bird/bird-template.conf", "r")
    template_text = bird_template.read()
    bird_template.close()

    template_text = template_text.replace("$KERNEL_TABLE_NUMBER", str(kernel_table_number))

    #Configure eBGP session with each provider    
    for provider in providers:
        remote_nodename = provider["id"]
        print(all_pops[remote_nodename])
        local_asn = local["as_number"]
        neighbor_ip = all_pops[remote_nodename]["ext-vpn-ip"]
        remote_asn = consts.SBAS_ASN
        out_prefixes = str(provider["out-prefixes"]).replace("'", "")

        ebgp_session = f'''
        protocol bgp {remote_nodename}01 {{
            local as {local_asn};
            neighbor {neighbor_ip} as {remote_asn};
            ipv4 {{
                table bgpannounce;
                import all;
                export filter {{
                    if source = RTS_STATIC then {{reject;}}
                    if net ~ {out_prefixes} then {{accept;}}
                    if source = RTS_BGP then {{accept;}}
                    reject;
                }};
            }};
            multihop;
        }}
        '''
        template_text = template_text + textwrap.dedent(ebgp_session)

   # Write bird configuration file
    bird_config = open("/etc/bird/bird.conf", "w")
    bird_config.write(template_text)
    bird_config.close()
    
