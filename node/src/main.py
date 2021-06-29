#!/usr/bin/env python3
import argparse
import sys
import signal

from src.config import sig
from src.config import wg
from src.system import routes
from src.config import bird
import time, threading

WAIT_TIME_SECONDS = 2
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

def start():
    # Configure system routes
    try:
        print("Setting up routes...")
        routes.setup()
        wg.start()
        bird.start()
        foo()
    except routes.RoutingError:
        print("Error during route setup. Cleaning up...")
        stop()
        sys.exit(1)
    
def stop():
    print("Removing routes...")
    routes.teardown()
    wg.stop()
    bird.stop()
    print("done.")

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
