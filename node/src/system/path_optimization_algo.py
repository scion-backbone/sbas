#!/usr/bin/env python3
import subprocess
import json
import ipaddress 
import os
import re
import requests

#TODO: change paths for importing packages before incorporating in sbas code
#import sys
#sys.path.append('/home/scionlab/sbas/node/src/')
#from config import parser 
#from config import consts
#from system import mrt_path_extraction

from src.config import parser
from src.config import consts
from src.system import mrt_path_extraction 

OPTIMIZED_TABLE = 7
OPTIMIZED_PRIORITY = 7
DIRECT_CONNECTION_COMMUNITY = 50
NEIGHBOR_CONNECTION_COMMUNITY = 100
UPDATE_PATH_PERIOD = 10

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


def bird_mrtdump_cleanup():
    try:
        mrtdump_path = consts.BIRD_MRTDUMP_DIR 
        bird_mrtdump_files = os.listdir(mrtdump_path)
        if bird_mrtdump_files:
            paths = [os.path.join(mrtdump_path, basename) for basename in bird_mrtdump_files]
            paths.sort(key = os.path.getctime, reverse=True)
            if len(paths) > 3:
                for path in paths[3:]:
                    try:
	                    os.remove(path)
                    except OSError as error:
	                    print("Error removing file " + path)    
    except:
        print('Provided directory is not existing')
        exit(1) 

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

def map_pop_ip_to_scion_address():
    ip_to_scion_address_dict = {}
    pop_nodes = parser.get_nodes()
    for name, node in pop_nodes.items():
        ip_to_scion_address_dict[node['secure-router-ip']] = {'scion_address': node['scion-ia'], 'nodename': name}
        #ip_to_scion_address_dict[node['secure-vpn-ip']] = {'scion_address': node['scion-ia'], 'nodename': name}
    return ip_to_scion_address_dict 
    
def get_current_scionpath_to_egress(dst_as):
    get_status = requests.get('http://127.0.0.1:30456/status')
    status_text = get_status.text
    pattern = f'''ISD-AS {dst_as}
  SESSION \d*, POLICY_ID \d*, REMOTE: \d*\.\d*\.\d*\.\d*:\d*, HEALTHY true
    PATHS:
      STATE                                        PATH
      -->                                          Hops: \[(.*)\] MTU: \d* NextHop: (.*):'''
    search_session = re.search(pattern, status_text)

    if search_session:
        paths =search_session.group(1) 
        path_hops = re.split(' \d*\>\d* ', paths)
        #print(path_hops)            
        return path_hops
    else:
        print('No matching session found for SCION destination AS')
        return None


def get_sbas_metric(path_hops_list):
    #TODO: add fetching of metric data for a path via SBAS to a PoP
    with open('../green_routing/scionAS_to_energy_mapping.json',  'r') as f:
        scionAS_to_energy = json.load(f)

    overall_green_GWh =0
    overall_total_GWh = 0

    for hop in path_hops_list:
        hop = hop.replace('16-','')
        if hop in scionAS_to_energy:
            green_pct = scionAS_to_energy[hop]['green_pct']
            hop_total = scionAS_to_energy[hop]['total_GWh'] 
            if green_pct:
                overall_green_GWh += green_pct * hop_total
            if hop_total:
                overall_total_GWh += hop_total 
        else:
            print('hop not found '+ hop)
    print(overall_total_GWh, overall_green_GWh)
    return overall_total_GWh, overall_green_GWh

def get_global_as_path_metric(path_hops_list):
    with open('../green_routing/asn_to_energy_mapping.json',  'r') as f:
        asn_to_energy = json.load(f)

    overall_green_GWh =0
    overall_total_GWh = 0 

    for hop in path_hops_list:
        hop_energy_mix = asn_to_energy.get(hop)
        if hop_energy_mix:
            green_pct = asn_to_energy[hop]['green_pct']
            hop_total = asn_to_energy[hop]['total_GWh'] 
            if green_pct:
                overall_green_GWh += green_pct * hop_total
            if hop_total:
                overall_total_GWh += hop_total 
        else:
            print('hop not found '+ hop)

    return overall_total_GWh, overall_green_GWh

def get_path_metric(global_path, next_hop, ip_to_scion_address):
    path_metric = 0
    number_of_hops = 0
    sbas_total_GWh = 0
    sbas_green_GWh = 0
    global_total_GWh = 0
    global_green_GWh = 0
    
    if next_hop in ip_to_scion_address: #goes via SBAS
        scion_address = ip_to_scion_address[next_hop]['scion_address']
        scion_path_hops = get_current_scionpath_to_egress(scion_address)
        sbas_total_GWh, sbas_green_GWh = get_sbas_metric(scion_path_hops)
        number_of_hops += len(scion_path_hops)

    
    if global_path != '':
        global_path_hops = global_path.split(' ')
        global_total_GWh, global_green_GWh = get_global_as_path_metric(global_path_hops)
        number_of_hops += len(global_path_hops)
    
    greenness = (sbas_green_GWh + global_green_GWh)/(sbas_total_GWh + global_total_GWh)
    print('path metric :'+ str(greenness))
    print('num hops : ' + str(number_of_hops))
    return greenness, number_of_hops

def update_best_path(best_path, checked_path, path_metric, gateway, num_hops, path_type= None):

    if (best_path['path_entry'] is None) or (path_metric > best_path['metric_total']) or (path_metric_total == best_path['metric_total'] and num_hops < best_path['number_of_hops']):
        best_path['path_entry'] = checked_path
        best_path['gateway'] = gateway
        best_path['number_of_hops'] = num_hops
        if path_type:
            best_path['type'] = path_type

    return best_path 

def install_routing_rule(dst_prefix, best_customer_option, best_secure_option, best_global_option, table_number):
    if best_customer_option['path_entry']:
        if best_customer_option['type'] == 'sbas_route':
            _run([
                "route", "add", 
                dst_prefix, "dev", best_customer_option['gateway'],                
                "table", str(table_number)
            ]) 
        elif best_customer_option['type'] == 'client_tunnel':
            _run([
                "route", "add", 
                dst_prefix, "via", best_customer_option['gateway'],    #TODO            
                "table", str(table_number)
            ]) 
        else:
            print('Unknown type of secure route given')  
    elif best_secure_option['path_entry'] :
        _run([  
            "route", "add", 
            dst_prefix, "dev", best_secure_option['gateway'],                
            "table", str(table_number)
        ])
    elif best_global_option['path_entry']:            
        _run([
            "route", "add", 
            dst_prefix, "via", best_global_option['gateway'],    #TODO            
            "table", str(table_number)
        ])  
                       
    else:
        print('No good path found for ' + dst_prefix) 

def optimized_path_selection():
    
    # 1) Flush routing table with optimized path selection
    try:
        _run(["route", "flush", "table", str(OPTIMIZED_TABLE)])
        while True: # need to call it multiple times, only one is deleted at a time
            _run(["rule", "del", "lookup", str(OPTIMIZED_TABLE)], silent=True)
    except:
        pass
    
    ip_to_scion_address = map_pop_ip_to_scion_address()
    secure_router_ip = parser.get_local_node()['secure-router-ip']
    sbas_asn = parser.get_sbas_asn()

    # 2) Read the latest BIRD mrtdump file and extract the available paths for each prefix
    newest_mrtdump_path = get_latest_bird_mrt_dump()
    prefix_to_paths_mapping = mrt_path_extraction.main(newest_mrtdump_path)

    # 3) Iterate over each prefix:
    for dst_prefix in prefix_to_paths_mapping.keys():
        available_paths = prefix_to_paths_mapping[dst_prefix]
        print(dst_prefix + '**********************************************')
        
        best_customer_option = {'path_entry': None, 'metric_total': None}
        best_secure_option = {'path_entry': None, 'metric_total': None}
        best_global_option = {'path_entry': None, 'metric_total': None}
        
        # 4) For each prefix, iterate over available paths
        for path_entry in available_paths:
            next_hop = path_entry.next_hop
            global_path = path_entry.path
            path_metric_total, number_of_hops = get_path_metric(global_path, next_hop, ip_to_scion_address)

            if path_entry.community_value == f'''{sbas_asn}:{DIRECT_CONNECTION_COMMUNITY}''':
                # If path to destination is direct client VPN tunnel
                best_customer_option = update_best_path(best_customer_option, path_entry, path_metric_total, path_entry.next_hop, number_of_hops, 'client_tunnel')       
            
            elif (path_entry.community_value == f'''{sbas_asn}:{NEIGHBOR_CONNECTION_COMMUNITY}''') and (next_hop in ip_to_scion_address):  
                # If path to destination is via a PoP that has direct connection to customer
                gateway = f"sbas-{ip_to_scion_address[next_hop]['nodename']}"        
                best_customer_option = update_best_path(best_customer_option, path_entry, path_metric_total, gateway, number_of_hops, 'sbas_route')       
            
            elif next_hop in ip_to_scion_address:
                #If path to destination goes through SBAS, but destination is not a customer                 
                gateway = f"sbas-{ip_to_scion_address[next_hop]['nodename']}"        
                best_secure_option = update_best_path(best_secure_option, path_entry, path_metric_total, gateway, number_of_hops, 'sbas_route')

            else:
                # Path goes via global path and not SBAS and destination is not a customer
                best_global_option = update_best_path(best_global_option, path_entry, path_metric_total, path_entry.next_hop, number_of_hops)
            
        install_routing_rule(dst_prefix, best_customer_option, best_secure_option, best_global_option, OPTIMIZED_TABLE)
        
    _run([
    "rule", "add",
    "from", "all",
    "lookup", str(OPTIMIZED_TABLE),
    "priority", str(OPTIMIZED_PRIORITY)
    ])
    
    bird_mrtdump_cleanup()

def make_periodic_call():
    """
    This function periodically runs the optimized path selection function.
    """
    my_timer = threading.Timer(UPDATE_PATH_PERIOD, make_periodic_call)
    my_timer.start()
    optimized_path_selection()
    return

if __name__ == '__main__':
    optimized_path_selection()