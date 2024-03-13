#!/usr/bin/env python3

import time
import pystemd.daemon
import sys
import signal


print("before this line the service is not really alive")
# lets extend the startuuptime by one second
pystemd.daemon.notify(False, EXTEND_TIMEOUT_USEC=10**6)

time.sleep(3)
# we still have one extra second.
pystemd.daemon.notify(False, ready=1)
