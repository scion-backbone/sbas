import json
import sys
import os

ENV_NODE = 'SBAS_NODE'

if ENV_NODE in os.environ:
    local = os.environ[ENV_NODE]

    path = sys.argv[1]
    ia = sys.argv[2]

    with open(path, 'r+') as f:
        cfg = json.load(f)
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
        f.seek(0)
        json.dump(cfg, f, indent=2)
        f.truncate()
else:
    print("Environment variable $SBAS_NODE not set.")
