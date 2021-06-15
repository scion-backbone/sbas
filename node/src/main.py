#!/usr/bin/env python3
import argparse
import sys

from src.config import sig
from src.config import containers
from src.config import wg
from src.system import routes
from src.config import bird

def configure():
    # Re-generate the assets that depend on SBAS topology / configuration
    sig.update()
    wg.setup()
    bird.setup()


def start():
    # Configure system routes
    try:
        print("Setting up routes...")
        routes.setup()
    except routes.RoutingError:
        print("Error during route setup. Cleaning up...")
        stop()
        sys.exit(1)
    
def stop():
    print("Removing routes...")
    routes.teardown()
    print("done.")

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
