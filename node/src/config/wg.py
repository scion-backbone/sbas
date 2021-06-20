from src.config import parser
import subprocess
# Length of external prefix space (e.g., "66.180.191.128/25")
EXTERNAL_PREFIX_LENGTH = 25

def setup():
    # Get local node IP address and prefix space configuration from nodes.json
    local = parser.get_local_node()
    
    # Read the template for the wireguard configuration file
    content = ""
    with open('src/config/wg0-template.conf', 'r') as f:
        content = f.read()
    
    # Replace placeholders for VPN Server IP address and VPN subnet with local configuration information
    for k, v in {
        'SBAS_VPN_SERVER_IP_NO_MASK': local['secure-vpn-ip'],
        'SBAS_VPN_NET': local['secure-subprefix'],
        'SBAS_VPN_SERVER_IP': local['secure-vpn-ip'] + '/' + str(EXTERNAL_PREFIX_LENGTH),
    }.items():
        content = content.replace(f"${k}", str(v))

    # Write configuration file for wg0 at appropriate path
    with open('/etc/wireguard/wg0.conf', 'w') as f:
        f.write(content)


def start():
    subprocess.run(["wg-quick", "up", "wg0"],
            stdout=subprocess.PIPE, # capture stdout
            stderr=subprocess.PIPE # capture stderr
    )


def stop():
    subprocess.run(["wg-quick", "down", "wg0"],
            stdout=subprocess.PIPE, # capture stdout
            stderr=subprocess.PIPE # capture stderr
    )