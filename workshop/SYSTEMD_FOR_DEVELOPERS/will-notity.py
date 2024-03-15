#!/usr/bin/env python3

import time
import pystemd.daemon

print("I will notify")
pystemd.daemon.notify(False, ready=1)

time.sleep(3)
print("Will this line be reach?")
