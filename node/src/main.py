#!/usr/bin/env python3
import argparse

def configure():
    pass

def start():
    print("Starting SBAS")

def stop():
    print("Stopping SBAS")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    args = parser.parse_args()

    if args.command == 'start':
        configure()
        start()
    elif args.command == 'stop':
        stop()
