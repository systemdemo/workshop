#!/usr/bin/env python3
# this is (almost) a carbon copy of https://raw.githubusercontent.com/lizrice/ebpf-beginners/main/packet.py

from bcc import BPF
from time import sleep
import socket

# Counts number of IP packets received per protocol on the eth0 interface

program = """
#include "packet.h"

BPF_HASH(packets);

int hello_packet(struct xdp_md *ctx) {
    u64 counter = 0;
    u64 key = 0;
    u64 *p;

    key = get_protocol(ctx);
    if (key != 0) {
        p = packets.lookup(&key);
        if (p != 0) {
            counter = *p;
        }
        counter++;
        packets.update(&key, &counter);
    }

    return XDP_PASS;
}
"""

b = BPF(text=program)
b.attach_xdp(dev="eth0", fn=b.load_func("hello_packet", BPF.XDP))

IP_PROTO = {
    socket.IPPROTO_ICMP: "ICMP",
    socket.IPPROTO_TCP: "TCP",
    socket.IPPROTO_UDP: "UDP",
}
try:
    while True:
        sleep(2)
        s = []
        for k, v in b["packets"].items():
            proto = IP_PROTO.get(k.value, k.value)
            s.append(f"Protocol {proto}: counter {v.value}")
        print(",".join(s))
except KeyboardInterrupt:
    b.remove_xdp(dev="eth0")
