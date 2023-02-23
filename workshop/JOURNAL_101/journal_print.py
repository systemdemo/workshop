#!/bin/python

import logging
import pystemd.journal

pystemd.journal.sendv(
  f"PRIORITY={logging.ERROR}",
  MESSAGE="Hello from pystemd journal printing",
  SYSLOG_IDENTIFIER="superuniqueid"
)
