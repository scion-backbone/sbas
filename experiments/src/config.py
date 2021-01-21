import json

NODES_PATH = "../nodes.json"
CUSTOMERS_PATH = "../customers.json"

def load_nodes():
    with open(NODES_PATH, 'r') as f:
        return json.load(f)

def load_customers():
    with open(CUSTOMERS_PATH, 'r') as f:
        return json.load(f)

