from src.config import parser

# Length of external prefix space (e.g., "66.180.191.128/25")
EXTERNAL_PREFIX_LENGTH = 25

def setup():
    # Get local node IP address and prefix space configuration from nodes.json
    local = parser.get_local_node()
    
    # Read the template for the wireguard configuration file
    wg_template = open('src/config/wg0-template.conf', 'r')
    content = wg_template.read()
    wg_template.close()
    
    # Replace placeholders for VPN Server IP address and VPN subnet with local configuration information
    for from, to in {
        'SBAS_VPN_SERVER_IP_NO_MASK': local['secure-vpn-ip'],
        'SBAS_VPN_NET': local['secure-subprefix'],
        'SBAS_VPN_SERVER_IP': local['secure-vpn-ip'] + '/' + str(EXTERNAL_PREFIX_LENGTH),
    }.items():
        content = content.replace(f"${from}", str(to))

    # Write configuration file for wg0 at appropriate path
    wg0_config = open('/etc/wireguard/wg0.conf', 'w')
    wg0_config.write(content)
    wg0_config.close()
