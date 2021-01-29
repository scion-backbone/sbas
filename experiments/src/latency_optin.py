import os
import sys
import shutil
from fabric import Connection
import csv
import math

from . import config as cfg
from .latency_nodes import get_shortest_scion_paths
from .parser import *

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
    ping_flags = "-c 10"
    PING_IP = "ping " + ping_flags
    PING_SCION = "scion ping " + ping_flags

    def get_out_path(suffix):
        return os.path.join(data_path, 'ping_' + suffix + '.' + cfg.OUT_EXT)

    def dump(conn, cmd, suffix):
        res = conn.run(cmd)
        if not res.ok:
            raise Exception
        with open(get_out_path(suffix), 'w') as f:
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
        dump(A_conn, f"{PING_IP} {B['public-ip']}", 'internet')

        # Connect customers to SBAS
        print("Connecting to SBAS...", end=' ')
        for X, conn in [(A, A_conn), (B, B_conn)]:
            setup(X, conn)
        print("done.")

        print("Recording ping through SBAS...")
        dump(A_conn, f"{PING_IP} {B['provider']['addr']}", 'sbas')

        print("Recording SCMP latency...")
        path_specs = get_shortest_scion_paths()
        seq = path_specs[(A['provider']['node'], B['provider']['node'])]
        seq_flag = f"--sequence '{' '.join(seq)}'"
        cmd = f"{PING_SCION} {ISP_B['scion-ia']},0.0.0.0 {seq_flag}"
        dump(ISP_A_conn, cmd, 'nodetonode')

        print("Recording latency through tunnels...")
        dump(A_conn, f"{PING_IP} {ISP_A['ext-vpn-ip']}", 'tunnelA')
        dump(B_conn, f"{PING_IP} {ISP_B['ext-vpn-ip']}", 'tunnelB')

    except:
        print("ERROR: removing output files")
        shutil.rmtree(data_path)
        sys.exit(1)
    finally:
        # Clean up connections
        for X, conn in [(A, A_conn), (B, B_conn)]:
            conn.run(f"cd sbas-proto/client && ./stop.sh {X['provider']['node']}")

    with open(os.path.join(data_path, 'data.csv'), 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(['link', 'avg', 'std'])

        data = {}
        for key in ['internet', 'sbas', 'tunnelA', 'tunnelB']:
            data[key] = parse_icmp_ping(get_out_path(key))
        data['nodetonode'] = parse_scmp_ping(get_out_path('nodetonode'))

        for key, (avg, std) in data.items():
            writer.writerow([key, avg, std])

        # Estimate overhead
        total_avg = 0
        total_var = 0
        for key in ['tunnelA', 'tunnelB', 'nodetonode']:
            avg, std = data[key]
            total_avg += avg
            total_var += std**2

        writer.writerow(['estimated', total_avg, math.sqrt(total_var)])

