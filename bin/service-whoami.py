#!/usr/bin/python


import os
import sys
import pystemd
import getpass
import pprint
import textwrap
from shutil import which
import time

def _(t):
    return textwrap.indent(t, prefix=" ")

MYPID = os.getpid()
with pystemd.systemd1.Manager() as m:
    unit_path = m.Manager.GetUnitByPID(MYPID)
    unit = pystemd.base.SDObject(b"org.freedesktop.systemd1", unit_path)
    unit.load()

print(
    """
/***
 *                          _                     _                           _ 
 *                         (_)                   | |                         (_)
 *      ___  ___ _ ____   ___  ___ ___  __      _| |__   ___   __ _ _ __ ___  _ 
 *     / __|/ _ \ '__\ \ / / |/ __/ _ \ \ \ /\ / / '_ \ / _ \ / _` | '_ ` _ \| |
 *     \__ \  __/ |   \ V /| | (_|  __/  \ V  V /| | | | (_) | (_| | | | | | | |
 *     |___/\___|_|    \_/ |_|\___\___|   \_/\_/ |_| |_|\___/ \__,_|_| |_| |_|_|
 *                                                                              
 *                                                                              
 */
"""
)

print(
    "#######################################",
    "starting service whoami",
    "runing as" ,
    _(f"Service Unit: {unit.Id.decode()}"),
    _(f"User: {getpass.getuser()}"),
    _(f"Extra: uid={os.getuid()} gid={os.getgid()}"),
    _(f"PID: {MYPID}"),
    _(f"MAINPID: {unit.Service.ExecMainPID if unit.Id.decode().endswith('service') else '<no main pid>'}"),
    "",
    "Environmental variables:",
    _(pprint.pformat({**os.environ})),
    sep="\n"
)


print("")
print("sleeping forever....")

# while True:
sys.stdout.flush()
os.execv(which("sleep"), ("sleep", "infinity"))
