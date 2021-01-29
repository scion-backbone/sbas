import os
import shutil
from fabric import Connection

from . import config as cfg
from .latency_nodes import get_shortest_scion_paths

def run(args, data_path):
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
    ISP_A_conn = Connection(ISP_A['public-ip'], user=cfg.SBAS_SSH_USER)
    print("done.")

    # Parameters
    ping_flags = "-c 3"
    PING_IP = "ping " + ping_flags
    PING_SCION = "scion ping " + ping_flags

    def dump(conn, cmd, filename):
        res = conn.run(cmd)
        if not res.ok:
            raise Exception
        with open(os.path.join(data_path, filename + '.' + cfg.OUT_EXT), 'w') as f:
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
        dump(A_conn, f"{PING_IP} {B['public-ip']}", "ping_internet")

        # Connect customers to SBAS
        print("Connecting to SBAS...", end=' ')
        for X, conn in [(A, A_conn), (B, B_conn)]:
            setup(X, conn)
        print("done.")

        print("Recording ping through SBAS...")
        dump(A_conn, f"{PING_IP} {B['provider']['addr']}", "ping_sbas")

        print("Recording SCMP latency...")
        path_specs = get_shortest_scion_paths()
        seq = path_specs[(A['provider']['node'], B['provider']['node'])]
        seq_flag = f"--sequence '{' '.join(seq)}'"
        cmd = f"{PING_SCION} {ISP_B['scion-ia']},0.0.0.0 {seq_flag}"
        dump(ISP_A_conn, cmd, "ping_scion")

        print("Recording latency through tunnels...")
        dump(A_conn, f"{PING_IP} {ISP_A['ext-vpn-ip']}", "ping_tunnelA")
        dump(B_conn, f"{PING_IP} {ISP_B['ext-vpn-ip']}", "ping_tunnelB")
    except:
        # Clean up
        print("ERROR: removing output files")
        for X, conn in [(A, A_conn), (B, B_conn)]:
            conn.run(f"cd sbas-proto/client && ./stop.sh {X['provider']['node']}")
        shutil.rmtree(data_path)

def process(args, data_path):
    pass

