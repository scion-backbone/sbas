import subprocess

from src.config import parser
from src.config import consts

# Routing tables
# - Secure customer prefixes
table_secure = 10
priority_secure = 10 # highest priority
# - Internet routing table
table_internet = 20
priority_internet = 20 # lowest priority

# NOTE: The SCION-IP gateway will also set up routes (default table)
internal_prefix_len = 24

# -> check the documentation for a complete picture!

class RoutingError(Exception):
    pass

def _run(iproute_cmd):
    try:
        result = subprocess.run(["ip"] + iproute_cmd)
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        raise RoutingError

def setup():
    local = parser.get_local_node()
    remotes = parser.get_remote_nodes()

    # 1) Set up internal SIG address
    #    - required for tunnel endpoints
    int_addr = f"{local['int-sig-ip']}/{internal_prefix_len}"
    _run(["addr", "add", int_addr, "dev", "sig"])

    # 2) Set up delivery to local customers across VPN tunnel
    #    - use secure prefix
    _run([
        "route", "add", local['ext-prefix'],
        "via", consts.VPN_GATEWAY_IP,
        "table", str(table_secure)
    ])
    _run([
        "rule", "add",
        "from", "all",
        "lookup", str(table_secure),
        "priority", str(priority_secure)
    ])

    # 3) Set up GRE tunnels to remote SBAS nodes
    #    - create a tunnel device "sbas-{node}" for each remote node
    #    - use internal SIG addresses as endpoints
    #    - route remote secure prefixes over the tunnel
    local_sig = local['int-sig-ip']
    for name, node in remotes.items():
        tunnel_dev = f"sbas-{name}"

        _run([
            "tunnel", "add", tunnel_dev, "mode", "gre",
            "remote", node['int-sig-ip'],
            "local", local_sig,
            "ttl", "255"
        ])
        _run(["link", "set", tunnel_dev, "up"])
        _run([
            "route", "add",
            node['ext-prefix'], "dev", tunnel_dev,
            "table", str(table_secure)
        ])

    # 4) Set up gateway for outbound Internet traffic
    #    - either deliver through local Internet gateway, or
    #    - route everything to a remote SBAS node that has an Internet gateway
    gateway = local['outbound-gateway']
    if gateway == consts.GATEWAY_LOCAL:
        # Default route with lowest priority
        _run([
            "route", "add",
            "0.0.0.0/0", "via", consts.INTERNET_GATEWAY_IP,
            "table", str(table_internet)
        ])
        for name in remotes:
            _run([
                "rule", "add",
                "iif", f"sbas-{name}",
                "lookup", str(table_internet),
                "priority", str(priority_internet)
            ])
    else:
        # Route all traffic from local customers to remote gateway
        _run([
            "route", "add",
            "0.0.0.0/0", "dev", "sbas-{gateway}",
            "table", str(table_internet)
        ])

    # Default rule for all traffic from local customers to Internet gateway
    _run([
        "rule", "add",
        "from", local['ext-prefix'],
        "lookup", str(table_internet),
        "priority", str(priority_internet)
    ])

def teardown():
    local = parser.get_local_node()
    remotes = parser.get_remote_nodes()

    # Remove addresses
    int_addr = f"{local['int-sig-ip']}/{internal_prefix_len}"
    try:
        _run(["addr", "del", int_addr, "dev", "sig"])
    except:
        pass

    # Remove GRE tunnels
    for name in remotes:
        try:
            _run(["tunnel", "del", f"sbas-{name}"])
        except:
            pass

    for table in [table_secure, table_internet]:
        # Flush routing tables
        _run(["route", "flush", "table", str(table)])

        # Delete rules that belong to this table
        _run(["rule", "del", "lookup", str(table)])
