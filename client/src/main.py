#!/usr/bin/env python3
import argparse
import sys

from src.vpn import wireguard
from src.bird import bird

def configure():
    # Re-generate the assets that depend on SBAS configuration
    wireguard.configure()

def start():
    wireguard.up()
    bird.setup()

def stop():
    wireguard.down()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    args = parser.parse_args()

    if args.command == 'start':
        # TODO: Detect if update is necessary (i.e., config is newer than last start)
        configure()
        start()
    elif args.command == 'stop':
        stop()
    elif args.command == 'configure':
        configure()
    else:
        print("Invalid command")
        sys.exit(1)
