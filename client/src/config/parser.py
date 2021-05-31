import os
import json

from src.config import consts

# Provides an interface to the SBAS configuration at {consts.ETC_DIR}.

cfg = {}
nodes = None

def get_config():
    global cfg
    if not cfg:
        with open(os.path.join(consts.ETC_DIR, consts.CFG_FILE), 'r') as f:
            cfg = json.load(f)
    return cfg

def get_nodes():
    global nodes
    if not nodes:
        with open(os.path.join(consts.ETC_DIR, consts.NODES_FILE), 'r') as f:
            nodes = json.load(f)
    return nodes

