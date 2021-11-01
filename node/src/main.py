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



WAIT_TIME_SECONDS = 3600
def configure():
    # Re-generate the assets that depend on SBAS topology / configuration
    sig.update()
    wg.setup()
    bird.setup()

def foo():
    print('this is my time' + str(time.ctime()))
    my_timer = threading.Timer(10, foo)
    my_timer.start()

    i = 0
    while i <10:
        i+=1
        time.sleep(1)
        print('sth')

    testfile = open('/home/scionlab/sbas/node/src/test.log', "a")
    testfile.write('this is my time' + str(time.ctime()))
    testfile.flush()
    testfile.close()
    return

def periodic_mrt_cleanup():
    my_timer = threading.Timer(WAIT_TIME_SECONDS, periodic_mrt_cleanup)
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
        ip = IPRoute()
        ip.route("add", dst="10.0.0.0", mask = 23, gateway = '66.180.191.130', table=8)
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
