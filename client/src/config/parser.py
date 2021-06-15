import os
import json

from src.config import consts

# Provides an interface to the SBAS configuration at {consts.ETC_DIR}.

cfg = {}
nodes = None
sbas_config = None

def get_config():
    global cfg
    if not cfg:
        with open(os.path.join(consts.ETC_DIR, consts.CFG_FILE), 'r') as f:
            cfg = json.load(f)
    return cfg

def get_nodes():
    global nodes
    if not nodes:
        nodes = get_sbas_config()["nodes"]
    return nodes

def get_sbas_config():
    global sbas_config
    if not sbas_config:
        with open(os.path.join(consts.ETC_DIR, consts.NODES_FILE), 'r') as f:
            sbas_config = json.load(f)
    return sbas_config

def get_sbas_asn():
    sbas_asn = get_sbas_config()["as-number"] 
    return sbas_asn       

