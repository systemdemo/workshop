#!/usr/bin/env python3

from bcc import BPF
from time import sleep
import ipaddress
from threading import Thread
from pathlib import Path
import ctypes
import atexit
import socket

FILTER_LIST = Path(__file__).parent / "deny"

# Counts number of IP packets received per protocol on the eth0 interface

program = """
#include "packet.h"

BPF_HASH(deny, u32, u32);

static inline bool should_filter(struct xdp_md *ctx)
{
    if (get_protocol(ctx) == 1) {
        u32 saddr_ = get_saddr(ctx);
        u32 * deny_saddr = deny.lookup(&saddr_);
        if (deny_saddr){
            return true;
        }
        return false;
    }
    return false;
}

int filter_packet(struct xdp_md *ctx) {
    if (should_filter(ctx)){
        return XDP_DROP;
    }
    return XDP_PASS;
}
"""


b = BPF(text=program)
b.attach_xdp(dev="eth0", fn=b.load_func("filter_packet", BPF.XDP))

try:
    while True:
        sleep(2)
        deny_hash = b["deny"]

        new = {ipaddress.ip_address(k.value): False for k in deny_hash}

        with FILTER_LIST.open() as filter_list_file:
            for filter_line in filter_list_file:

                if not (filter_line := filter_line.strip()):
                    continue

                ipaddr = ipaddress.ip_address(filter_line.strip())
                new[ipaddr] = True

        for ipaddr, should_block in new.items():
            ck = ctypes.c_uint(int(ipaddr))
            if should_block:
                deny_hash[ck] = ck
            else:
                deny_hash.pop(ck)
except KeyboardInterrupt:
    b.remove_xdp("eth0")
