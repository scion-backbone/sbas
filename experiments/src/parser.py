import re

def parse_icmp_ping(path):
    with open(path, 'r') as f:
        result = f.readlines()[-1]
        r = re.compile('.* = ' + '/'.join(['(\d+\.?\d*)']*4) + ' ms')
        matches = r.match(result)
        avg = float(matches.group(1))
        std = float(matches.group(4))
        return avg, std

def parse_scmp_ping(path):
    with open(path, 'r') as f:
        avg = 0
        std = 0
        return avg, std

