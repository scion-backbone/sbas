import json

SBAS_SSH_USER = 'scionlab'
OUT_EXT = 'out'

NODES_PATH = "../nodes.json"
CUSTOMERS_PATH = "../customers.json"

nodes = None
customers = None

def get_nodes():
    global nodes
    if nodes is None:
        with open(NODES_PATH, 'r') as f:
            nodes = json.load(f)
    return nodes

def get_customers():
    global customers
    if customers is None:
        with open(CUSTOMERS_PATH, 'r') as f:
            customers = json.load(f)
    return customers

