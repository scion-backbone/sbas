import subprocess

from src.config import parser
from src.config import consts

def setup():
    def run(cmd):
        result = subprocess.run(["ip"] + cmd)
        result.check_returncode()

    local = parser.get_local_node()
    remotes = parser.get_remote_nodes()

    # Set up route to local customers
    run(["route", "add", local['ext-prefix'], "via", consts.VPN_GATEWAY_IP, "table", "10"])
    run(["rule", "add", "from", "all", "lookup", "10", "priority", "10"])

    # Set up GRE tunnels
    local_sig = local['int-sig-ip']
    for name, node in remotes.items():
        dev = f"sbas-{name}"

        run([
            "tunnel", "add", dev, "mode", "gre",
            "remote", node['int-sig-ip'],
            "local", local_sig,
            "ttl", "255"
        ])
        run(["link", "set", dev, "up"])
        run(["route", "add", node['ext-prefix'], "dev", dev, "table", "10"])

    # Set up outbound gateway
    gateway = local['outbound-gateway']
    # Allow other nodes to use this as outbound gateway
    if gateway == consts.GATEWAY_LOCAL:
        run(["route", "add", "0.0.0.0/0", "via", consts.INTERNET_GATEWAY_IP, "table", "20"])
        rule_number = 20
        for name in remotes:
            run(["rule", "add", "iif", f"sbas-{name}", "lookup", "20", "priority", str(rule_number)])
            rule_number += 1
    # Route traffic to remote gateway
    else:
        run(["route", "add", "0.0.0.0/0", "dev", "sbas-{gateway}", "table", "15"])
        run(["rule", "add", "from", local['ext-prefix'], "lookup", "15", "table", "15"])

def teardown():
    def run(cmd):
        subprocess.run(["ip"] + cmd)

    local = parser.get_local_node()
    remotes = parser.get_remote_nodes()

    for name in remotes:
        run(["tunnel", "del", f"sbas-{name}"])

    run(["route", "flush", "table", "15"])
