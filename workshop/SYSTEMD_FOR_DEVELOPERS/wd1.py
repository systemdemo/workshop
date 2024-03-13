#!/usr/bin/env python3

import time
import pystemd.daemon

print("before this line the service is not really alive")
pystemd.daemon.notify(False, ready=1)
print("Ok we are alive, lets see the life interval")

watchdog_usec = pystemd.daemon.watchdog_enabled()

print(f"must ping systemd at most {watchdog_usec / 10**6}s")

for i in range(10):
    # sleeping for half the time
    time.sleep(watchdog_usec / 10**6 / 10)

    pystemd.daemon.notify(False, watchdog=1)
    print("Will this line be reach?")

print("time to exit!")
