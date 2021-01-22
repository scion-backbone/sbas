import os
import shutil
from fabric import Connection

import src.config as cfg

SBAS_SSH_USER = 'scionlab'
OUT_EXT = 'out'

def RunLatencyCustomers(args, data_path):
    customers = cfg.get_customers()
    A = customers[args.src]
    B = customers[args.dst]

    nodes = cfg.get_nodes()
    ISP_A = nodes[A['provider']['node']]
    ISP_B = nodes[B['provider']['node']]

    # Set up SSH connections
    print("Connecting to remotes...", end=' ')
    A_conn = Connection(A['public-ip'], user=A['ssh-user'])
    B_conn = Connection(B['public-ip'], user=B['ssh-user'])
    # ISP_A_conn = Connection(ISP_A['public-ip'], user=SBAS_SSH_USER)
    # ISP_B_conn = Connection(ISP_B['public-ip'], user=SBAS_SSH_USER)
    print("done.")

    # Parameters
    ping_flags = "-c 3"
    PING = "ping " + ping_flags

    def dump(conn, cmd, filename):
        res = conn.run(cmd)
        if not res.ok:
            raise Exception
        with open(os.path.join(data_path, filename + '.' + OUT_EXT), 'w') as f:
            f.write(res.stdout)

    def setup(X, conn):
        ISP = X['provider']
        cmds = [
            f"cd sbas-proto/client",
            f"sudo ./install.sh {ISP['node']} {ISP['addr']}",
            f"./start.sh {ISP['node']}",
        ]
        res = conn.run(" && ".join(cmds))
        if not res.ok:
            raise Exception

    try:
        # Baselines
        print("Recording Internet baseline...")
        dump(A_conn, f"{PING} {B['public-ip']}", "ping_internet")

        # Connect customers to SBAS
        print("Connecting to SBAS...", end=' ')
        for X, conn in [(A, A_conn), (B, B_conn)]:
            setup(X, conn)
        print("done.")

        print("Recording ping through SBAS...")
        dump(A_conn, f"{PING} {B['provider']['addr']}", "ping_sbas")
    except:
        # Clean up
        print("ERROR: removing output files")
        for X, conn in [(A, A_conn), (B, B_conn)]:
            conn.run(f"cd sbas-proto/client && ./stop.sh {X['provider']['node']}")
        shutil.rmtree(data_path)

def RunLatencyNodes(args, data_path):
    nodes = cfg.get_nodes()

    ping_flags = "-c 5"
    PING_SCION = "scion ping " + ping_flags
    PING_IP = "ping " + ping_flags

    def measure(A, B):
        A_conn = Connection(nodes[A]['public-ip'], user=SBAS_SSH_USER)

        def dump(cmd, suffix):
            res = A_conn.run(cmd)
            if not res.ok:
                raise Exception
            with open(os.path.join(data_path, f"{A}_{B}_{suffix}.{OUT_EXT}"), 'w') as f:
                f.write(res.stdout)

        dump(f"{PING_SCION} {nodes[B]['scion-ia']},0.0.0.0", "scion")
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

