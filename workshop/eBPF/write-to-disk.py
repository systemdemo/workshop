#!/usr/bin/env python3

LOGGING_PREFIX= "#"*10

print("MYFLAG")

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO ASIGN A VARIABLE")
filename = "/tmp/not-exists"
print()

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO open {filename}")
file_= open(filename, "w")
print()


print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO write TO {filename}")
file_.write("42")
print()

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO flush {filename}")
file_.flush()
print()

print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO close {filename}")
file_.close()
print()