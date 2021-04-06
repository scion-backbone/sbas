#!/usr/bin/env python3
import argparse
import sys

from src.config import sig
from src.config import containers
from src.system import routes
from src.system import docker

def configure():
    # Re-generate the assets that depend on SBAS topology / configuration
    sig.update()
    containers.update()
    docker.build()

def start():
    # Start the Docker container
    docker.up()
    # Configure system routes
    try:
        routes.setup()
    except routes.RoutingError:
        print("Error during route setup")
        stop()
        sys.exit(1)

def stop():
    docker.down()
    routes.teardown()

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
