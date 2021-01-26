import os
import shutil
from fabric import Connection

from . import config as cfg

def run(args, data_path):
    nodes = cfg.get_nodes()

    ping_flags = "-c 5"
    PING_SCION = "scion ping " + ping_flags
    PING_IP = "ping " + ping_flags

    # Currently using a workaround for paths
    # (the SCMP ping tool picks a path at random -> manually take the shortest one)
    path_specs_def = {
        ('oregon', 'frankfurt'): ['16']*4,
        ('oregon', 'tokyo'): ['16']*4,
        ('oregon', 'singapore'): ['16']*4,
        ('frankfurt', 'singapore'): ['16']*4,
        ('frankfurt', 'tokyo'): ['16']*5,
        ('tokyo', 'singapore'): ['16']*4
    }
    # Assuming symmetrical path lengths
    path_specs = dict(path_specs_def)
    for (A, B) in path_specs_def:
        path_specs[(B, A)] = path_specs_def[(A, B)]

    def measure(A, B):
        A_conn = Connection(nodes[A]['public-ip'], user=SBAS_SSH_USER)

        def dump(cmd, suffix):
            res = A_conn.run(cmd)
            if not res.ok:
                raise Exception
            with open(os.path.join(data_path, f"{A}_{B}_{suffix}.{OUT_EXT}"), 'w') as f:
                f.write(res.stdout)

        seq_str = ' '.join(path_specs[(A, B)])
        seq_flag = f"--sequence '{seq_str}'"
        dump(f"{PING_SCION} {nodes[B]['scion-ia']},0.0.0.0 {seq_flag}", "scion")
        dump(f"{PING_IP} {nodes[B]['public-ip']}", "ip")

    src_list = nodes
    dst_list = nodes

    if args.src:
        src_list = [args.src]
    if args.dst:
        dst_list = [args.dst]

    for A in src_list:
        for B in dst_list:
            if A != B:
                measure(A, B)

def process(args, data_path):
    pass

