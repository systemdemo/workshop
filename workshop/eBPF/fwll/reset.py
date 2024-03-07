#!/usr/bin/env python3

from bcc import BPF
from time import sleep
import ipaddress
from threading import Thread
from pathlib import Path
import ctypes
import atexit

# Counts number of IP packets received per protocol on the eth0 interface

program = """

static inline bool should_filter(struct xdp_md *ctx){
    return false;
}

int hello_packet(struct xdp_md *ctx) {
    if (should_filter(ctx)){
        return XDP_DROP;
    }
    return XDP_PASS;
}
"""


b = BPF(text=program)
b.attach_xdp(dev="eth0", fn=b.load_func("hello_packet", BPF.XDP))

atexit.register(b.remove_xdp, "eth0")
