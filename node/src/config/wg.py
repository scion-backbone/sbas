from src.config import parser

# Length of external prefix space (e.g., "66.180.191.128/25")
external_prefix_length = 25

def setup():
    # Get local node IP address and prefix space configuration from nodes.json
    local = parser.get_local_node()
    
    # Read the template for the wireguard configuration file
    wg_template = open('src/config/wg0-template.conf', 'r')
    template_text = wg_template.read()
    wg_template.close()
    
    # Replace placeholders for VPN Server IP address and VPN subnet with local configuration information
    template_text = template_text.replace('$SBAS_VPN_SERVER_IP_NO_MASK', local['ext-vpn-ip'])
    template_text = template_text.replace('$SBAS_VPN_NET', local['ext-prefix'])
    template_text = template_text.replace('$SBAS_VPN_SERVER_IP', local['ext-vpn-ip'] + '/' + str(external_prefix_length))

    # Write configuration file for wg0 at appropriate path
    wg0_config = open('/etc/wireguard/wg0.conf', 'w')
    wg0_config.write(template_text)
    wg0_config.close()
