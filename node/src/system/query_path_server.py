import subprocess
import json

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



#Step 1. Find type of destination
# a. SCION node
# b. Opt-In Customer
# c. Legacy AS

scion_dst = "16-ffaa:0:1009" #frankfurt scion address


#If SCION node:
#1. Get list of available paths to scion destination
paths = get_available_scion_paths(scion_dst)
#2. Relate paths to metric database
#3. Sort paths and pick top 1

#If Opt-In Customer
#1. Get PoPs connected to customer
#2. Run subprocess scion showpaths {PoP address} for each PoP
#3. Save all paths in an array
#4. Relate SCION segments to metric database
#5. Relate customer tunnel to metric database
#6. Add metrics of the different path sections together (within SCION + VPN tunnel)
#7. Sort paths and pick top 1

#If Legacy AS
#1. 

