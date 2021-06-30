import subprocess
import json
import ipaddress 
import parser
from src.system import mrt_path_extraction

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



def path_optimization_per_prefix(dst_addr):
    #Step 1. Find type of destination
    # a. SCION node
    # b. Customer
    # c. External

    if type_of_destination == "secure":
        #If Secure (SCION) node:
        #1. Get list of available paths to scion destination
        paths = get_available_scion_paths(scion_dst)
        #2. Relate paths to metric database 
        #3. Sort paths and pick top 1

    elif type_of_destination == "customer":
        #If Customer
        #1. Get PoPs connected to customer
        #I will have to get the routes from the mrt file and see potential routes
        #2. Run subprocess scion showpaths {PoP address} for each PoP
        for egress_pop in potential_pops:
            paths = get_available_scion_paths(egress_pop)

        #3. Save all paths in an array
        #4. Relate SCION segments to metric database
        #5. Relate customer tunnel to metric database (in case the opt-in customer is connected to more than one PoPs)
        #6. Combine the metric data for both path sections (within-SCION + VPN tunnel)
        #7. Sort paths and pick top 1

    elif type_of_destination == "external":
        #If External AS
        #1. Get PoPs that have paths towards the destination from mrt file?
        #2. Get list of scion paths to potential egress PoPs
        for egress_pop in potential_pops:
            paths = get_available_scion_paths(egress_pop)
        #3. Relate SCION segments to metric database
        #4. Get the AS-level path that is outside SCION (connecting potential egress PoPs to destination)
        #5. Relate the external path segments to metric database
        #6. Combine the metric data for both path sections (within-SCION + external BGP path)
        #7. Sort paths and pick top 1
        
    else:
        print("Wrong type of destination was provided (" + type_of_destination + ").")

def path_optimization():
    path_dict = mrt_path_extraction.main()
    for dst_prefix in path_dict:
        available_paths = path_dict[dst_prefix]
        path_optimization_per_prefix(dst_prefix)    

path_optimization()