#!/usr/bin/env python3

import time
import pystemd.daemon
import sys
import signal


def exit_handler(signal, frame):
    print(f"going to exit because I got {signal}")
    sys.exit(0)


signal.signal(signal.SIGABRT, exit_handler)

print("before this line the service is not really alive")
pystemd.daemon.notify(False, ready=1)
print("Ok we are alive, lets see the life interval")


pystemd.daemon.notify(
    False, watchdog="trigger"
)  # this should trigger watchdog right away

time.sleep(10)
