import json
from src.config import parser

# Generates the SIG configuration file that depends on the SBAS topology.

RULE_FILE = '/etc/scion/sig.json'

def _update_rules():
    remotes = parser.get_remote_nodes()

    with open(RULE_FILE, 'w') as f:
        cfg = {'ConfigVersion': 9001}
        cfg['ASes'] = {
            remote['scion-ia']: {'Nets': [f"{remote['internal-prefix']}"]}
            for remote in remotes.values()
        }
        f.write(json.dumps(cfg, indent=2, sort_keys=True))

def update():
    _update_rules()
