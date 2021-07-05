import subprocess
import json
import ipaddress 
import os

#TODO: change paths for importing packages before incorporating in sbas code
import sys
sys.path.append('/home/scionlab/sbas/node/src/')
from config import parser 
from config import consts
from system import mrt_path_extraction

#from src.config import parser
#from src.config import consts
#from src.system import mrt_path_extraction 

table_optimized = 15
priority_optimized = 15

class RoutingError(Exception):
    pass

def _run(iproute_cmd, silent=False):
    try:
        subprocess.run(
            ['sudo'] + ["ip"] + iproute_cmd, #TODO check if sudo is necessary
            stdout=subprocess.PIPE, # capture stdout
            stderr=subprocess.PIPE, # capture stderr
            check=True # raise exception on failure
        )
    except subprocess.CalledProcessError as e:
        if silent:
            pass
        print(f"Command failed: {' '.join(e.cmd)} -> \"{str(e.output)}\"")
        raise RoutingError


def get_latest_bird_mrt_dump():
    try:
        mrtdump_path = consts.BIRD_MRTDUMP_DIR 
        bird_mrtdump_files = os.listdir(mrtdump_path)
        if bird_mrtdump_files:
            paths = [os.path.join(mrtdump_path, basename) for basename in bird_mrtdump_files]
            return max(paths, key=os.path.getctime)
    except:
        print('Provided directory is not existing')
        exit(1)

def get_available_scion_paths(scion_destination):
    """Function that finds the available SCION paths from the running node to a SCION destination.

       Input args:
       scion_destination: string that contains the SCION address of the destination node (e.g "16-ffaa:0:1009")

       Output: List of available paths to destination SCION node. Each path is a dictionary with the keys: 
       "fingerprint" (string), 
       "hops" (list), 
       "next_hops" (string),
       "expiry" (string), 
       "mtu": integer, 
       "latency" (list), 
       "status" (string), 
       "local_ip" (string)
    """
    
    try:
        #1. Run subprocess scion showpaths {SCION Destination address}
        available_paths_bytes = subprocess.check_output("scion showpaths " + scion_destination + " -j", stderr=subprocess.STDOUT, shell=True)
        
        #2. Save all paths in an array
        available_paths_string = available_paths_bytes.decode("utf8")
        available_paths_json = json.loads(available_paths_string)
        available_paths_list = available_paths_json["paths"]
    
    except subprocess.CalledProcessError as e:
        #If there are no scion paths available, return empty list
        print(f"Command failed: {' '.join(e.cmd)} -> \"{str(e.output)}\"")
        available_paths_list = []

    return available_paths_list

def map_pop_ip_to_scion_address():
    ip_to_scion_address_dict = {}
    pop_nodes = parser.get_nodes()
    for name, node in pop_nodes.items():
        ip_to_scion_address_dict[node['secure-router-ip']] = {'scion_address': node['scion-ia'], 'nodename': name}
        #ip_to_scion_address_dict[node['secure-vpn-ip']] = {'scion_address': node['scion-ia'], 'nodename': name}
    return ip_to_scion_address_dict 
    
def get_as_metric(asn):
    #TODO: add fetching of metric data for an AS
    return 1

def get_metric_to_pop(pop_ip_address):
    #TODO: add fetching of metric data for a path via SBAS to a PoP
    return 1

def get_global_as_path_metric(as_path):
    global_path_metric = 0
    as_path_list = as_path.split(' ')

    for asn in as_path_list:
       global_path_metric += get_as_metric(asn)

    return global_path_metric


def path_optimization():
    '''
    # 1) Flush routing table with optimized path selection
    _run(["route", "flush", "table", str(table_optimized)])
    # Delete rules that belong to this table
    try:
        while True: # need to call it multiple times, only one is deleted at a time
            _run(["rule", "del", "lookup", str(table_optimized)], silent=True)
    except:
        pass
    '''
    ip_to_scion_address = map_pop_ip_to_scion_address()
    newest_mrtdump_path = get_latest_bird_mrt_dump()
    path_dict = mrt_path_extraction.main(newest_mrtdump_path)

    for dst_prefix in path_dict:
        available_paths = path_dict[dst_prefix]
        print(dst_prefix)

        best_sbas_option = {'path_entry': None, 'metric_total': None}
        best_global_option = {'path_entry': None, 'metric_total': None}

        for path_entry in available_paths:
            next_hop = path_entry.next_hop
            print(path_entry)
            path_metric_total = 0
            path = path_entry.path
            print(path)
            if next_hop in ip_to_scion_address:
                #must go through sbas before exiting and we need to find the best egress PoP
                
                #scion_paths = get_available_scion_paths(ip_to_scion_address[next_hop]['scion_address'])
                if path == '':
                    # Destination is within SBAS (most likely a PoP)
                    path_metric_total = get_metric_to_pop(next_hop)
                else:
                    # Extract external AS path and get the total metric value
                    path_metric_total = get_metric_to_pop(next_hop) + get_global_as_path_metric(path)
                    
                # Check if the new path for this prefix has a better metric value than the previous "via SBAS" ones and update accordingly
                if (best_sbas_option['path_entry'] is None) or (path_metric_total < best_sbas_option['metric_total']):
                    best_sbas_option['metric_total'] = path_metric_total
                    gateway = f"sbas-{ip_to_scion_address[next_hop]['nodename']}"        
                    best_sbas_option['path_entry'] = path_entry
                    best_sbas_option['gateway'] = gateway 
            else:
                # Path goes via the VPN client or BGP client and not SBAS
                
                path_metric_total = get_global_as_path_metric(path)

                # Check if the new path for this prefix has a better metric value than the previous "non-SBAS" ones and update accordingly
                if (best_global_option['path_entry'] is None) or (path_metric_total < best_global_option['metric_total']):
                    best_global_option['metric_total'] = path_metric_total
                    best_global_option['path_entry'] = path_entry
                    #TODO: must find gateway      
                    #best_global_option['gateway'] = '' 
                
        # Add routing rule for prefix in custom table
        if best_sbas_option['path_entry'] :
            print('here')
            '''
            _run([
                "route", "add", 
                dst_prefix, "dev", best_sbas_option['gateway'],                
                "table", str(table_optimized)
            ])  
            '''
        elif best_global_option['path_entry']:
            print('im here')
            '''
            _run([
                "route", "add", 
                dst_prefix, "via", best_global_option['gateway'],    #TODO            
                "table", str(table_optimized)
            ])  
            '''            
        else:
            print('No good path found for ' + dst_prefix)
     



path_optimization()