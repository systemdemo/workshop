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

IP_PROTO = {
    socket.IPPROTO_ICMP: "ICMP",
    socket.IPPROTO_TCP: "TCP",
    socket.IPPROTO_UDP: "UDP",
}

# Counts number of IP packets received per protocol on the eth0 interface

program = """
#include "packet.h"

BPF_PERF_OUTPUT(events);
BPF_HASH(deny, u32, u32);

struct addrs {
    u64 proto;
    u32	sa;
    u32	da;
};


static inline u64 submit_to_userspace(struct xdp_md *ctx)
{
    if (get_protocol(ctx) == 1){
        struct addrs myaddrs = {};
        myaddrs.proto = get_protocol(ctx);
        myaddrs.sa = get_saddr(ctx);
        myaddrs.da = get_daddr(ctx);

        events.perf_submit(ctx, &myaddrs, sizeof (struct addrs) );
    }
    return 0;
}

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

int hello_packet(struct xdp_md *ctx) {
    submit_to_userspace(ctx);
    if (should_filter(ctx)){
        return XDP_DROP;
    }
    return XDP_PASS;
}
"""


def reload(b: BPF) -> None:

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


def process_event(cpu, data, size):
    event = b["events"].event(data)
    print(
        IP_PROTO.get(event.proto),
        ipaddress.ip_address(event.sa),
        "->",
        ipaddress.ip_address(event.da),
    )


b = BPF(text=program)

b.attach_xdp(dev="eth0", fn=b.load_func("hello_packet", BPF.XDP))
atexit.register(b.remove_xdp, "eth0")


b["events"].open_perf_buffer(process_event)

t = Thread(target=reload, args=(b,))
t.start()

while True:
    b.perf_buffer_poll()
