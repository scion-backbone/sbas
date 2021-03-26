#!/usr/bin/env python3
import argparse
import sys

from . import config
from .system import tunnels
from .system import docker

def configure():
    config.sig.update()
    config.containers.update()
    # TODO: Build Docker container

def start():
    docker_env = config.containers.get_env()
    docker.up(docker_env)
    tunnels.setup()

def stop():
    docker.down()
    tunnels.teardown()

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
