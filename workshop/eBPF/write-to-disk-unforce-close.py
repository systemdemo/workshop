#!/usr/bin/env python3
import sys

LOGGING_PREFIX = "#" * 10

print("MYFLAG")

filename = "/tmp/not-exists"
file_ = open(filename, "w")

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO write TO {filename}")
file_.write("42")
print()

sys.exit(0)
