import json
import sys
import os

ENV_NODE = 'SBAS_NODE'

if ENV_NODE in os.environ:
    local = os.environ[ENV_NODE]

    path = sys.argv[1]
    ia = sys.argv[2]

    with open(path, 'r') as f:
        cfg = json.loads(f.read())
        cfg['SIG'] = {
            f"sig{ia}-1": {
                'Addrs': {
                    'IPv4': {
                        'Public': {
                            'Addr': "127.0.0.1",
                            'L4Port': 31056
                        }
                    }
                }
            }
        }
        f.write(json.dumps(cfg, indent=2, sort_keys=True))
else:
    print("Environment variable $SBAS_NODE not set.")
