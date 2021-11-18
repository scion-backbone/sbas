#!/usr/bin/python
import json
from mrtparse import *
from collections import namedtuple

prefix_entry = namedtuple("prefix_entry", 'next_hop as_path communities')

def parse_mrt_file(file_name):
    """This function reads an MRT file and parses through the stored BGP announcements.
    It iterates over each received prefix announcement and for each prefix, it maps it to
    all the available paths. Specifically, the extracted information for each path is the
    next hop, the AS path and the assigned community values.

    Input:
    - file_name: The path to the MRT file to be parsed

    Output:
    - prefix_to_paths_mapping: A dictionary mapping each prefix to a list of "prefix entries" named
    tuples that contain the next hop, AS path and community values for each available path.
    """
    i = 0
    prefix_to_paths_mapping = {}
    for entry in Reader(file_name):
        if i != 0:
            announcement_data= entry.data
            prefix = announcement_data['prefix']
            prefix_length = announcement_data['prefix_length']
            dst_prefix = str(prefix) +'/'+str(prefix_length)
            rib_entries = announcement_data['rib_entries']

            for rib_entry in rib_entries:
                next_hop = None
                as_path = None
                communities = []

                path_attributes = rib_entry['path_attributes']
                for attribute in path_attributes:
                    if 'NEXT_HOP' in attribute['type']:
                        next_hop = attribute['value']
                    elif 'AS_PATH' in attribute['type']:
                        for entry in attribute['value']:
                            if 'AS_SEQUENCE' in entry['type']:
                                as_path = entry['value']
                                break
                    elif 'COMMUNITY' in attribute['type']:
                        communities = attribute['value']

                    if next_hop and as_path and (len(communities)>0):
                        break

                if next_hop and as_path:
                    new_path = prefix_entry(next_hop, as_path, communities)

                    if dst_prefix not in prefix_to_paths_mapping.keys():
                        prefix_to_paths_mapping[dst_prefix] = [new_path]
                    elif new_path not in prefix_to_paths_mapping[dst_prefix]:
                        prefix_to_paths_mapping[dst_prefix].append(new_path)

        i +=1
    return prefix_to_paths_mapping