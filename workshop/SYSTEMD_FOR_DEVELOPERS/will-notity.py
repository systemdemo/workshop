#!/usr/bin/env python3

import time
import pystemd.daemon

print("I will notify")
pystemd.daemon.notify(False, ready=1)

pystemd.daemon.notify(False, watchdog=1, WATCHDOG_USEC=)


time.sleep(3.5)
print("Will this line be reach?")
