#!/usr/bin/env python3
import json
import sys
import os

path = sys.argv[1]

with open(path, 'r+') as f:
    cfg = json.load(f)
    cfg['sigs'] = {
        f"sig-1": { # TODO: Determine these addresses dynamically
            "ctrl_addr": "172.31.6.223:30256",
            "data_addr": "172.31.6.223:30056" 
        }
    }
    f.seek(0)
    json.dump(cfg, f, indent=2)
    f.truncate()
