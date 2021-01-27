import re
from statistics import mean, stdev

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
        r = re.compile('time=(\d+\.?\d*)ms')
        xs = []
        for line in f.readlines():
            m = r.search(line)
            if m:
                xs.append(float(m.group(1)))
        avg = mean(xs)
        std = stdev(xs)
        return avg, std

