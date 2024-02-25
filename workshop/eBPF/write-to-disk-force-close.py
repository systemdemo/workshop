#!/usr/bin/env python3

# This calls write, but instead of exiting cleanly, it executes os._exit that exit python ASAP
# if python is managing the buffer for the file, then calling os._exit will not flush to disk
# but if its "something else" whats keeping the buffer, then that something else should flush
# the content and we would see it. spoiler alert... its python.

import os


LOGGING_PREFIX= "#"*10

print("MYFLAG")

filename = "/tmp/not-exists"
file_ = open(filename, "w")

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO write TO {filename}")
file_.write("42")
print()

os._exit(0)