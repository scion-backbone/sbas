import os
import subprocess

from src.config import parser

WIREGUARD_CFG_DIR = '/etc/wireguard'
WG_PORT = 55555

cfg = parser.get_config()
providers = cfg['providers']

def _gen_config(provider):
    name = provider['id']

    private_key = '4I4dAr6iIKKuDPHIMMq81vxxW3Gyaam0vxfiaGLNqn8='

    lines = [
        "[Interface]",
        f"PrivateKey = {private_key}",
        f"Address = {provider['local']}/32",
        "ListenPort = 55556",
        "\n[Peer]",
        f"PublicKey = {provider['vpn-key']}",
        f"AllowedIPs = {', '.join(provider['out-prefixes'])}",
        f"Endpoint = {provider['public-ip']}:{WG_PORT}",
        "PersistentKeepalive = 25"
    ]

    path = os.path.join(WIREGUARD_CFG_DIR, f"wg0-{name}.conf")
    with open(path, 'w') as f:
        for l in lines:
            f.write(l + '\n')
    os.chmod(path, 600)

def configure():
    for provider in providers:
        _gen_config(provider)

def up():
    for provider in providers:
        subprocess.run(["wg-quick", "up", f"wg0-{provider['id']}"], check=True)

def down():
    for provider in providers:
        subprocess.run(["wg-quick", "down", f"wg0-{provider['id']}"], check=True)
