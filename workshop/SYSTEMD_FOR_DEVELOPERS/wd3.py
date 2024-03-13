#!/usr/bin/env python3

import time
import pystemd.daemon
import sys
import signal

# def exit_handler(signal, frame):
#     print(f"going to exit because I got {signal}")
#     sys.exit(0)
# signal.signal(signal.SIGABRT, exit_handler)

print("before this line the service is not really alive")
pystemd.daemon.notify(False, ready=1)
print("Ok we are alive, lets see the life interval")

watchdog_usec = pystemd.daemon.watchdog_enabled()

# lets ping and lets add an extra second to watchdog
pystemd.daemon.notify(False, watchdog=1, watchdog_usec=watchdog_usec + 10**6)
time.sleep(watchdog_usec / 10**6)
print("we should still have a whole extra second to spear")
