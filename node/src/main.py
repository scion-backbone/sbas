#!/usr/bin/env python3
import argparse
import sys
import signal

from src.config import sig
from src.config import wg
from src.system import routes
from src.config import bird
import time, threading
from src.system import optimized_path_selection
from src.config import consts
from pyroute2 import IPRoute


MRT_CLEANUP_PERIOD = 3600
OPTIMIZED_PATH_SELECTION_PERIOD = 21600
def configure():
    # Re-generate the assets that depend on SBAS topology / configuration
    sig.update()
    wg.setup()
    bird.setup()

def periodic_optimized_path_selection():
    """
    Periodically run the optimized path selection algorithm
    """
    my_timer = threading.Timer(OPTIMIZED_PATH_SELECTION_PERIOD, foo)
    my_timer.start()
    print("Running Optimized Path Selection Algorithm")
    optimized_path_selection.optimized_path_selection()
    return

def periodic_mrt_cleanup():
    """
    Periodically cleanup the directory where MRT files are generated by
    BIRD to conserve disk space
    """
    my_timer = threading.Timer(MRT_CLEANUP_PERIOD, periodic_mrt_cleanup)
    my_timer.start()
    print('sth')
    optimized_path_selection.bird_mrtdump_cleanup()
    return

def start():
    # Configure system routes
    try:
        print("Setting up routes...")
        routes.setup()
        wg.start()
        bird.start()
        #periodic_optimized_path_selection #Remove comment when optimized path selection is ready to be incorporated in the system
        periodic_mrt_cleanup()
    except routes.RoutingError:
        print("Error during route setup. Cleaning up...")
        stop()
        sys.exit(1)

def stop():
    print("Removing routes...")
    routes.teardown()
    wg.stop()
    bird.stop()

def graceful_stop(sig, frame):
    stop()
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, graceful_stop)

    if args.command == 'start':
        # TODO: Detect if update is necessary (i.e., config is newer than last start)
        configure()
        start()
    elif args.command == 'configure':
        configure()
    else:
        print("Invalid command")
        sys.exit(1)
