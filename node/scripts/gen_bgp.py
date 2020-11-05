import json
import os
from gen_functions import *


if __name__ == "__main__":
    with open(CFG_FILE, 'r') as f:
        nodes = json.loads(f.read())
        gen_sshconfig(nodes)

        if ENV_NODE in os.environ:
            local_id = os.environ[ENV_NODE]
            if local_id in nodes:
                local = nodes[local_id]
                remote = nodes.copy()
                remote.pop(local_id)

                gen_sig_rules(remote)
                gen_docker_env(local)
                gen_routes_bgp(local, remote)
            else:
                print(f"Node '{local_id}' does not exist")
