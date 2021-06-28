#!/usr/bin/env python

import sys, argparse, copy
from datetime import *
from mrtparse import *
from collections import namedtuple
peer = None
prefix_entry = namedtuple("prefix_entry", 'origin peer_as peer_ip next_hop path')

def parse_args():
    p = argparse.ArgumentParser(
        description='This script converts to bgpdump format.')
    p.add_argument(
        '-t', dest='ts_format', default='dump', choices=['dump', 'change'],
        help='timestamps for RIB dumps reflect the time of the dump \
            or the last route modification(default: dump)')
    p.add_argument(
        'path_to_file',
        help='specify path to MRT format file')
    return p.parse_args()

class BgpDump:

    def __init__(self, args):
        self.ts_format = args.ts_format
        self.type = ''
        self.num = 0
        self.ts = 0
        self.org_time = 0
        self.flag = ''
        self.peer_ip = ''
        self.peer_as = 0
        self.nlri = []
        self.withdrawn = []
        self.as_path = []
        self.origin = ''
        self.next_hop = []
        self.local_pref = 0
        self.med = 0
        self.comm = ''
        self.atomic_aggr = 'NAG'
        self.aggr = ''
        self.as4_path = []
        self.as4_aggr = ''
        self.old_state = 0
        self.new_state = 0
        self.available_paths = {}

    def add_available_path(self, prefix, next_hop):
        new_entry = prefix_entry(self.origin, self.peer_as, self.peer_ip, next_hop, self.merge_as_path())
        if self.available_paths.get(prefix):
            if new_entry not in self.available_paths[prefix]:
                self.available_paths[prefix].append(new_entry)
        else:
            self.available_paths[prefix] = [new_entry]
        """
        if self.flag == 'B' or self.flag == 'A':
            self.output.write(
                '%s|%s|%s|%s|%s|%s|%s|%s' % (
                    self.type, d, self.flag, self.peer_ip, self.peer_as, prefix,
                    self.merge_as_path(), self.origin
                )
            )
            self.output.write('\n')
          
        elif self.flag == 'W':
             self.output.write(
                    '%s|%s|%s|%s|%s|%s\n' % (
                    self.type, d, self.flag, self.peer_ip, self.peer_as,
                    prefix
                )
            )
        elif self.flag == 'STATE':
            self.output.write(
            '%s|%s|%s|%s|%s|%d|%d\n' % (
                self.type, d, self.flag, self.peer_ip, self.peer_as,
                self.old_state, self.new_state
                )
            )
        """

    def withdraw_path(self, prefix):
        if self.available_paths.get(prefix):
            routes_to_be_removed = set()
            for entry in self.available_paths.get(prefix):
                if (self.origin == entry.origin) and (self.peer_as == entry.peer_as) and (self.peer_ip == entry.peer_ip):
                    routes_to_be_removed.add(entry)
            self.available_paths[prefix] = list(set(self.available_paths.get(prefix)).difference(routes_to_be_removed))	
			
    def update_routes(self):
        for withdrawn in self.withdrawn:
            if self.type == 'BGP4MP':
                self.flag = 'W'
            self.withdraw_path(withdrawn)
        for nlri in self.nlri:
            if self.type == 'BGP4MP':
                self.flag = 'A'
            for next_hop in self.next_hop:
                self.add_available_path(nlri, next_hop)
    """
    def td(self, m, count):
        self.type = 'TABLE_DUMP'
        self.flag = 'B'
        self.ts = m['timestamp'][0]
        self.num = count
        self.org_time = m['originated_time'][0]
        self.peer_ip = m['peer_ip']
        self.peer_as = m['peer_as']
        self.nlri.append('%s/%d' % (m['prefix'], m['prefix_length']))
        for attr in m['path_attributes']:
            self.bgp_attr(attr)
        self.update_routes()
    """
    def td_v2(self, m):
        global peer
        self.type = 'TABLE_DUMP2'
        self.flag = 'B'
        #self.ts = m['timestamp'][0]
        if m['subtype'][0] == TD_V2_ST['PEER_INDEX_TABLE']:
            peer = copy.copy(m['peer_entries'])
        elif (m['subtype'][0] == TD_V2_ST['RIB_IPV4_UNICAST']
            or m['subtype'][0] == TD_V2_ST['RIB_IPV4_MULTICAST']
            or m['subtype'][0] == TD_V2_ST['RIB_IPV6_UNICAST']
            or m['subtype'][0] == TD_V2_ST['RIB_IPV6_MULTICAST']):
            self.num = m['sequence_number']
            self.nlri.append('%s/%d' % (m['prefix'], m['prefix_length']))
            for entry in m['rib_entries']:
                self.org_time = entry['originated_time'][0]
                self.peer_ip = peer[entry['peer_index']]['peer_ip']
                self.peer_as = peer[entry['peer_index']]['peer_as']
                self.as_path = []
                self.origin = ''
                self.next_hop = []
                self.local_pref = 0
                self.med = 0
                self.comm = ''
                self.atomic_aggr = 'NAG'
                self.aggr = ''
                self.as4_path = []
                self.as4_aggr = ''
                for attr in entry['path_attributes']:
                    self.bgp_attr(attr)
                self.update_routes()
    """
    def bgp4mp(self, m, count):
        self.type = 'BGP4MP'
        self.ts = m['timestamp'][0]
        self.num = count
        self.org_time = m['timestamp'][0]
        self.peer_ip = m['peer_ip']
        self.peer_as = m['peer_as']
        if (m['subtype'][0] == BGP4MP_ST['BGP4MP_STATE_CHANGE']
            or m['subtype'][0] == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
            self.flag = 'STATE'
            self.old_state = m['old_state'][0]
            self.new_state = m['new_state'][0]
            #self.print_line([], '')
        elif (m['subtype'][0] == BGP4MP_ST['BGP4MP_MESSAGE']
            or m['subtype'][0] == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
            or m['subtype'][0] == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
            or m['subtype'][0] == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
            if m['bgp_message']['type'][0] != BGP_MSG_T['UPDATE']:
                return
            for attr in m['bgp_message']['path_attributes']:
                self.bgp_attr(attr)
            for withdrawn in m['bgp_message']['withdrawn_routes']:
                self.withdrawn.append(
                    '%s/%d' % (
                        withdrawn['prefix'], withdrawn['prefix_length']
                    )
                )
            for nlri in m['bgp_message']['nlri']:
                self.nlri.append(
                    '%s/%d' % (
                        nlri['prefix'], nlri['prefix_length']
                    )
                )
            self.update_routes()
    """
    def bgp_attr(self, attr):
        if attr['type'][0] == BGP_ATTR_T['ORIGIN']:
            self.origin = ORIGIN_T[attr['value']]
        elif attr['type'][0] == BGP_ATTR_T['NEXT_HOP']:
            self.next_hop.append(attr['value'])
        elif attr['type'][0] == BGP_ATTR_T['AS_PATH']:
            self.as_path = []
            for seg in attr['value']:
                if seg['type'][0] == AS_PATH_SEG_T['AS_SET']:
                    self.as_path.append('{%s}' % ','.join(seg['value']))
                elif seg['type'][0] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as_path.append('(' + seg['value'][0])
                    self.as_path += seg['value'][1:-1]
                    self.as_path.append(seg['value'][-1] + ')')
                elif seg['type'][0] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as_path.append('[%s]' % ','.join(seg['value']))
                else:
                    self.as_path += seg['value']
            """      
            elif attr['type'][0] == BGP_ATTR_T['MULTI_EXIT_DISC']:
                self.med = attr['value']
            elif attr['type'][0] == BGP_ATTR_T['LOCAL_PREF']:
                self.local_pref = attr['value']
            elif attr['type'][0] == BGP_ATTR_T['ATOMIC_AGGREGATE']:
                self.atomic_aggr = 'AG'
            elif attr['type'][0] == BGP_ATTR_T['AGGREGATOR']:
                self.aggr = '%s %s' % (attr['value']['as'], attr['value']['id'])
            elif attr['type'][0] == BGP_ATTR_T['COMMUNITY']:
                self.comm = ' '.join(attr['value'])
            """
        elif attr['type'][0] == BGP_ATTR_T['MP_REACH_NLRI']:
            self.next_hop = attr['value']['next_hop']
            if self.type != 'BGP4MP':
                return
            for nlri in attr['value']['nlri']:
                self.nlri.append(
                    '%s/%d' % (
                        nlri['prefix'], nlri['prefix_length']
                    )
                )	
        elif attr['type'][0] == BGP_ATTR_T['MP_UNREACH_NLRI']:
            if self.type != 'BGP4MP':
                return
            for withdrawn in attr['value']['withdrawn_routes']:
                self.withdrawn.append(
                    '%s/%d' % (
                        withdrawn['prefix'], withdrawn['prefix_length']
                    )
                )
        elif attr['type'][0] == BGP_ATTR_T['AS4_PATH']:
            self.as4_path = []
            for seg in attr['value']:
                if seg['type'][0] == AS_PATH_SEG_T['AS_SET']:
                    self.as4_path.append('{%s}' % ','.join(seg['value']))
                elif seg['type'][0] == AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                    self.as4_path.append('(' + seg['value'][0])
                    self.as4_path += seg['value'][1:-1]
                    self.as4_path.append(seg['value'][-1] + ')')
                elif seg['type'][0] == AS_PATH_SEG_T['AS_CONFED_SET']:
                    self.as4_path.append('[%s]' % ','.join(seg['value']))
                else:
                    self.as4_path += seg['value']
        elif attr['type'][0] == BGP_ATTR_T['AS4_AGGREGATOR']:
            self.as4_aggr = '%s %s' % (
                attr['value']['as'], attr['value']['id']
            )

    def merge_as_path(self):
        if len(self.as4_path):
            n = len(self.as_path) - len(self.as4_path)
            return ' '.join(self.as_path[:n] + self.as4_path)
        else:
            return ' '.join(self.as_path)

    def merge_aggr(self):
        if len(self.as4_aggr):
            return self.as4_aggr
        else:
            return self.aggr

def main():
    args = parse_args()
    d = Reader(args.path_to_file)
    count = 0
    route_list = {}
    for m in d:
        if m.err:
            continue
        b = BgpDump(args)
        """
        if m.data['type'][0] == MRT_T['TABLE_DUMP']:
            print('type table dump')
            exit()
            b.td(m.data, count)
        """
        if m.data['type'][0] == MRT_T['TABLE_DUMP_V2']:
            b.td_v2(m.data)
            """
            elif m.data['type'][0] == MRT_T['BGP4MP']:
                print('type bgp4mp')
                exit()
                b.bgp4mp(m.data, count)
            """
        else:
            print('Entry in wrong format.')
            continue
        
        for key in b.available_paths:

            if key not in route_list:
                route_list[key] = b.available_paths[key]
            else:
                route_list[key] = list(set(route_list[key]) | set(b.available_paths[key]))
        count += 1
        
    print(route_list)
    return route_list
if __name__ == '__main__':
    main()
