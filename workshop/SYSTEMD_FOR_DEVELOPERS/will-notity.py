#!/usr/bin/env python3

import time
import pystemd.daemon

print("I refuse to notify")
pystemd.daemon.notify(False, ready=1)

time.sleep(3.5)
print("Will this line be reach?")
