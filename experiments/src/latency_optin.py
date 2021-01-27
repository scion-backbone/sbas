import os
from fabric import Connection

from . import config as cfg

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
    print("done.")

    # Parameters
    ping_flags = "-c 3"
    PING = "ping " + ping_flags

    def dump(conn, cmd, filename):
        res = conn.run(cmd)
        if not res.ok:
            raise Exception
        with open(os.path.join(data_path, filename + '.' + cfg.OUT_EXT), 'w') as f:
    # ISP_B_conn = Connection(ISP_B['public-ip'], user=SBAS_SSH_USER)
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

def process(args, data_path):
    pass

