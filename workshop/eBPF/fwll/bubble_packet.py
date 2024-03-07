#!/usr/bin/env python3

from bcc import BPF
import ipaddress
import ctypes
import socket

IP_PROTO = {
    socket.IPPROTO_ICMP: "ICMP",
    socket.IPPROTO_TCP: "TCP",
    socket.IPPROTO_UDP: "UDP",
}

# Counts number of IP packets received per protocol on the eth0 interface

program = """
#include "packet.h"

BPF_PERF_OUTPUT(events);

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

int bubble_packet(struct xdp_md *ctx) {
    submit_to_userspace(ctx);
    return XDP_PASS;
}
"""

b = BPF(text=program)

b.attach_xdp(dev="eth0", fn=b.load_func("bubble_packet", BPF.XDP))


@b["events"].open_perf_buffer
def process_event(cpu, data, size):
    event = b["events"].event(data)
    print(
        IP_PROTO.get(event.proto),
        ipaddress.ip_address(event.sa),
        "->",
        ipaddress.ip_address(event.da),
    )


try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    b.remove_xdp("eth0")
