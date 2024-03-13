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

print(f"must ping systemd at most {watchdog_usec / 10**6}s")

# lets actually hang
time.sleep(watchdog_usec / 10**6 + 10)
# by now we shold be dead
