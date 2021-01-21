import src.config as cfg

def RunLatencyCustomers(args, data_path):
    customers = cfg.load_customers()
    src = customers[args.src]
    dst = customers[args.dst]

    nodes = cfg.load_nodes()
    src_node = nodes[src['provider-main']]
    dst_node = nodes[dst['provider-main']]

    # Start customer connections

def RunLatencyNodes(args, data_path):
    nodes = cfg.load_nodes()
    src = nodes[args.src]
    dst = nodes[args.dst]

