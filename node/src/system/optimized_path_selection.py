import subprocess
import json
import ipaddress
import os
import re
import requests
import random
import datetime
#TODO: change paths for importing packages before incorporating in sbas code
import sys
sys.path.append('/home/scionlab/sbas/node/src/')
from config import parser
from config import consts
from system import mrt_parser
from pyroute2 import IPRoute

DIRECTLY_CONNECTED_ROUTE_TAG = 50
INTERNAL_ROUTE_TAG = 100
OPTIMIZED_TABLE = 7
OPTIMIZED_PRIORITY = 7

NUMBER_OF_SAMPLES = 840000
rrc = 'RRC06'

#cached_sbas_hops = {'16-ffaa:0:100a':['16-ffaa:0:100b', '16-ffaa:0:1006', '16-ffaa:0:1007', '16-ffaa:0:100a'],'16-ffaa:0:1009': ['16-ffaa:0:100b', '16-ffaa:0:1006', '16-ffaa:0:1005', '16-ffaa:0:1001', '16-ffaa:0:1009'],'16-ffaa:0:1008':['16-ffaa:0:100b', '16-ffaa:0:1006', '16-ffaa:0:1005', '16-ffaa:0:1008']}
cached_sbas_hops = {}
with open('../green_routing/scionAS_to_energy_mapping.json',  'r') as f:
    scionAS_to_energy = json.load(f)

with open('../green_routing/asn_to_energy_mapping.json',  'r') as f:
    asn_to_energy = json.load(f)

class RoutingError(Exception):
    pass

def _run(iproute_cmd, silent=False):
    try:
        subprocess.run(
            ["ip"] + iproute_cmd, #TODO check if sudo is necessary
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
    return ip_to_scion_address_dict

def get_current_scionpath_to_egress(dst_as):
    global cached_sbas_hops

    if dst_as in cached_sbas_hops.keys():
        return cached_sbas_hops[dst_as]
    else:
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
            cached_sbas_hops[dst_as] = path_hops
            return path_hops
        else:
            print('No matching session found for SCION destination AS')
            return None

def get_sbas_metric(path_hops_list):
    global scionAS_to_energy

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

    return overall_total_GWh, overall_green_GWh


def get_global_as_path_metric(path_hops_list):
    global asn_to_energy
    overall_green_GWh =0
    overall_total_GWh = 0

    for hop in path_hops_list:
        if hop in asn_to_energy.keys():
            hop_energy_mix = asn_to_energy[hop]
        else:
            hop_energy_mix = asn_to_energy['default']

        green_pct = hop_energy_mix['green_pct']
        hop_total = hop_energy_mix['total_GWh']
        if green_pct:
            overall_green_GWh += green_pct * hop_total
        if hop_total:
            overall_total_GWh += hop_total

    return overall_total_GWh, overall_green_GWh

def get_path_metric(global_path, next_hop, ip_to_scion_address):
    path_metric = 0
    number_of_hops = 0
    sbas_total_GWh = 0
    sbas_green_GWh = 0
    global_total_GWh = 0
    global_green_GWh = 0

    if next_hop in ip_to_scion_address: #Path through SBAS
        scion_address = ip_to_scion_address[next_hop]['scion_address']
        scion_path_hops = get_current_scionpath_to_egress(scion_address)
        if scion_path_hops:
            sbas_total_GWh, sbas_green_GWh = get_sbas_metric(scion_path_hops)
            number_of_hops += len(scion_path_hops)
        else:
            print('no hops for ' + str(next_hop))

    if len(global_path)>0: #There is an external portion in the path
        global_total_GWh, global_green_GWh = get_global_as_path_metric(global_path)
        number_of_hops += len(global_path)

    if (sbas_total_GWh + global_total_GWh) > 0:
        greenness = (sbas_green_GWh + global_green_GWh)/(sbas_total_GWh + global_total_GWh)
    else:
        greenness = 0
    return greenness, number_of_hops

def update_best_path(best_path, checked_path, path_metric, gateway, num_hops):
    if (path_metric > best_path['metric_total']) or (path_metric == best_path['metric_total'] and num_hops < best_path['number_of_hops']):
        best_path['path_entry'] = checked_path
        best_path['gateway'] = gateway
        best_path['number_of_hops'] = num_hops
        best_path['metric_total'] = path_metric
    return best_path

def install_routing_rule(ip, dst_prefix, best_customer_option, best_external_option, table_number):
    try:
        pref_split = dst_prefix.split('/')
        pref = pref_split[0]
        masks = int(pref_split[1])
        if best_customer_option['path_entry']:
            ip.route("add", dst=pref, mask = masks, gateway = best_customer_option['gateway'], table=table_number)
        elif best_external_option['path_entry']:
            ip.route("add", dst=pref, mask = masks, gateway = best_external_option['gateway'], table=table_number)
        else:
            print('No good path found for ' + dst_prefix)
    except Exception as e:
        print('issue with prefix ' + str(dst_prefix))
        print(str(e))

def optimized_path_selection():
    # 1) Initialize necessary parameters
    #start = datetime.datetime.now()
    ip_to_scion_address = map_pop_ip_to_scion_address()
    secure_router_ip = parser.get_local_node()['secure-router-ip']
    sbas_asn = parser.get_sbas_asn()
    newest_mrtdump_path = get_latest_bird_mrt_dump()

    # 2) Read the latest BIRD mrtdump file and extract the available paths for each prefix
    prefix_to_paths_mapping = mrt_parser.parse_mrt_file(newest_mrtdump_path)

    print(len(prefix_to_paths_mapping.keys()))
    sampled_prefixes = random.sample(list(prefix_to_paths_mapping), NUMBER_OF_SAMPLES)
    #print((datetime.datetime.now() - start).total_seconds())

    #start = datetime.datetime.now()
    # 3) Flush routing table with optimized path selection
    try:
        _run(["route", "flush", "table", str(OPTIMIZED_TABLE)])
        while True: # need to call it multiple times, only one is deleted at a time
            _run(["rule", "del", "lookup", str(OPTIMIZED_TABLE)], silent=True)
    except:
        pass

    #print((datetime.datetime.now() - start).total_seconds())

    # 4) Iterate over each prefix:
    #start = datetime.datetime.now()
    ip = IPRoute()

    for dst_prefix in sampled_prefixes:
        available_paths = prefix_to_paths_mapping[dst_prefix]
        best_customer_option = {'path_entry': None, 'metric_total':0, 'number_of_hops': float('inf')}
        best_external_option = {'path_entry': None, 'metric_total':0, 'number_of_hops': float('inf')}

        # 5) For each prefix, iterate over available paths
        for path_entry in available_paths:
            next_hop = path_entry.next_hop
            external_path = path_entry.as_path
            path_metric_total, number_of_hops = get_path_metric(external_path, next_hop, ip_to_scion_address)
            if ((f'''{sbas_asn}:{DIRECTLY_CONNECTED_ROUTE_TAG}''' in path_entry.communities) or ((f'''{sbas_asn}:{INTERNAL_ROUTE_TAG}''' in path_entry.communities) and (next_hop in ip_to_scion_address))):
                # If path to destination is direct customer VPN tunnel or connection to another PoP that is directly connected to customer
                best_customer_option = update_best_path(best_customer_option, path_entry, path_metric_total, path_entry.next_hop, number_of_hops)
            else:
                # Path goes via global path, not through SBAS, and destination is not a customer
                best_external_option = update_best_path(best_external_option, path_entry, path_metric_total, path_entry.next_hop, number_of_hops)
        # 6) Install Routing rule using the optimized chosen path
        install_routing_rule(ip, dst_prefix, best_customer_option, best_external_option, OPTIMIZED_TABLE)

    #end = (datetime.datetime.now() - start).total_seconds()
    #print(f'''sample_size: {NUMBER_OF_SAMPLES}, runtime: {(datetime.datetime.now() - start).total_seconds()}''')
    #with open('runtime_results2.txt',  'a') as f:
    #    f.write('number of samples: ' + str(NUMBER_OF_SAMPLES) + ', duration: ' + str(end) + '\n')

    # 7) Add lookup to the routing table
    _run([
    "rule", "add",
    "from", "all",
    "lookup", str(OPTIMIZED_TABLE),
    "priority", str(OPTIMIZED_PRIORITY)
    ])

    # 8) Cleanup the directory where BIRD mrt files are stored, to conserve disk space
    bird_mrtdump_cleanup()

if __name__ == '__main__':
    optimized_path_selection()