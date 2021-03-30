#!/usr/bin/env python3
import json
import sys
import os

path = sys.argv[1]

with open(path, 'r+') as f:
    cfg = json.load(f)
    ctrl_addr = cfg['control_service']['cs-1']['addr']
    ctrl_ip = ctrl_addr.split(':')[0]
    cfg['sigs'] = {
        f"sig-1": {
            "ctrl_addr": f"{ctrl_ip}:30256",
            "data_addr": f"{ctrl_ip}:30056" 
        }
    }
    f.seek(0)
    json.dump(cfg, f, indent=2)
    f.truncate()
