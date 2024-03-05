
Now that we have a good understanding of what syscalls are, and how to monitor them, it's time to dive a bit more in the world of eBPF.

eBPF can be used  for networking, observability and security; we will focus mostly on observability.

In this section, we will not dive much into the in and out, but we will explore a couple of tools that come with bcc-tools. A few caveats before we start. 



1. If you are running this inside a container, there are chances that this will not work, or… will not work as expected, containers and kernel space have a very rocky relationship, so for this section if you do it on a vm, it will probably work.
2. This will definitely not work on vanilla podman on macos and windows, as the vm image used for this is super lock down. we prefer vm for this on this OS, which means that m1/m2 users are out.

Ok, let's get started…


# Exploring bcc-tools

BCC stand for BPF Compiler collection,  is a toolset based on eBPF technology that allows you to analyze both OS and 
network performance of Linux distributions with ease.

/usr/share/bcc/tools/ is full of a bunch of useful scripts that you can use in your analysis.
However, the best thing about them is that they are all written in python and are very simple to understand… 
You can use them as learning materials.
Let's see a couple:

## execsnoop

perhaps the most famous one its execsnoop, this, without any arguments, will tell you
what gets executed (execve calls) in the entire system, to call it just run:


```
[root@7ece76c6d931 workshop]# /usr/share/bcc/tools/execsnoop 
```

A bunch of garbage is sent to stderr/out from compiling something (no worries,  
we will understand that part later)...


```
In file included from /virtual/main.c:14:
In file included from include/uapi/linux/ptrace.h:183:
In file included from arch/x86/include/asm/ptrace.h:5:
In file included from arch/x86/include/asm/segment.h:7:
arch/x86/include/asm/ibt.h:77:8: warning: 'nocf_check' attribute ignored; use -fcf-protection to enable the attribute [-Wignored-attributes]
extern __noendbr u64 ibt_save(bool disable);
       ^
arch/x86/include/asm/ibt.h:32:34: note: expanded from macro '__noendbr'
#define __noendbr       __attribute__((nocf_check))
                                       ^
arch/x86/include/asm/ibt.h:78:8: warning: 'nocf_check' attribute ignored; use -fcf-protection to enable the attribute [-Wignored-attributes]
extern __noendbr void ibt_restore(u64 save);
       ^
arch/x86/include/asm/ibt.h:32:34: note: expanded from macro '__noendbr'
#define __noendbr       __attribute__((nocf_check))
                                       ^
2 warnings generated.
```

Then you finally start getting some data



```
PCOMM            PID     PPID    RET ARGS                                                                                                                                                                                                      
solo_collector   1214474 1         0 /opt/chef-solo/bin/solo_collector --bundle_name cpe_init --verbose                                                                                                                                                                                                                                                           
systemd-userwor  1214496 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
systemd-userwor  1214495 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
systemd-userwor  1214497 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
git              1214529 1052931   0 /usr/share/gitkraken/resources/app.asar.unpacked/git/bin/git -c gpg.format=openpgp -c tag.gpgSign=0 -c commit.gpgSign=0 -c fetch.prune=1 -c gpg.program=gpg -c credential.helper= -c safe.directory=* -c g
c.auto=0 -c gpg.ssh.program=ssh-keygen -c                                                                                                                                                                     
```


This app, monitor all the execs that happen on your system, there is no 
“sampling here”, so everything that get executed will show up here, go on, 
open a new terminal and execute something like “ls -ll” and see the line that pops 
up is  


```
ls               1214798 1210099   0 /bin/ls --color=auto -ll
```


Fascinating to see what is going on.

You can see the code by inspecting /usr/share/bcc/tools/execsnoop, but we live in the 21st century, and we can see it in GitHub [here](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py) . We can inspect relevant parts are, the [c eBPF code](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py#L116-L235) and the [python userspace code](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py#L305-L344) .


## tcpconnect

If you want to monitor what network calls get done, you can with tcpconnect

```
/usr/share/bcc/tools/tcpconnect -d 
...
Tracing connect ... Hit Ctrl-C to end                                                                                                                                                                                                          
PID     COMM         IP SADDR            DADDR            DPORT                                                                                                                                                                                
5733    Chrome_Child 6  2620:10d:c085:2103:ccf2:4833:b033:8fbc 2a03:2880:f031:15:face:b00c:0:420d 443                                                                                                                                          
482045  IOThreadPool 6  ::1              ::1              1456                                                                                                                                                                                 
482045  IOThreadPool 6  ::1              ::1              1456                                                                                                                                                                                 
2797    ScheduledSrv 4  127.0.0.1        127.0.0.1        4244   
36402   connectEvb   6  2620:10d:c085:2103:ccf2:4833:b033:8fbc 2a03:2880:f031:e1:face:b00c:0:434e 443    
36402   connectEvb   4  172.26.26.189    157.240.22.223   443    
   
```


open another terminal and execute `wget google.com -O-`, you'll see a new line like

```
485785  wget         6  2620:10d:c085:2103:ccf2:4833:b033:8fbc 2607:f8b0:4005:80e::200e 80     
485785  wget         6  2620:10d:c085:2103:ccf2:4833:b033:8fbc 2607:f8b0:4005:802::2004 80
```

This looks very familiar to tcpdump, and yes, it is very familiar, the only difference is that 
this is written in python and straightforward to read... all it does its hook itself to a 
few syscalls that you can see [here](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/tcpconnect.py#L531-L538) 
... What's interesting is how you can hook to `udp_recvmsg` and `udpv6_queue_rcv_one_skb` to snoop DNS queries.

## tcplife

On the same line as tcpdump,
a nice little helper it's called [tcplife](https://github.com/iovisor/bcc/blob/master/tools/tcplife.py).
This one helps track the lifespan and throughput of a TCP Session. go on and execute it

```commandline
/usr/share/bcc/tools/tcplife
...
PID   COMM       LADDR           LPORT RADDR           RPORT TX_KB RX_KB MS
12759 sshd       192.168.56.101  22    192.168.56.1    60639     2     3 1863.82
12783 sshd       192.168.56.101  22    192.168.56.1    60640     3     3 9174.53
12844 wget       10.0.2.15       34250 54.204.39.132   443      11  1870 5712.26
12851 curl       10.0.2.15       34252 54.204.39.132   443       0    74 505.90
```

execute a `wger google.com -O-` on another terminal and see it there... at this point I want to adress the concern of 
"wait, i already can sniff network with tcpdump, why do i want to know this". A good answer is provided by
[this article](https://opensource.com/article/17/11/bccbpf-performance)

> Before you say: "Can't I just scrape tcpdump(8) output for this?" note that running tcpdump(8), or any packet sniffer, can cost noticable overhead on high packet-rate systems, even though the user- and kernel-level mechanics of tcpdump(8) have been optimized over the years (it could be much worse). tcplife doesn't instrument every packet; it only watches TCP session state changes for efficiency, and, from that, it times the duration of a session. It also uses kernel counters that already track throughput, as well as process and command information ("PID" and "COMM" columns), which are not available to on-the-wire-sniffing tools like tcpdump(8).

## opensnoop

There are three ways of opening a file ([`open`](https://man7.org/linux/man-pages/man2/open.2.html), [`openat`](https://man7.org/linux/man-pages/man2/open.2.html) and [`openat2`](https://man7.org/linux/man-pages/man2/openat2.2.html)… 
yes deprecating things is hard). There is "snoop" that can undertand all 3 and answer the question "what files hsa been open" 
its name its Opensnoop, and it monitors all 3, so no matter how a process wants to open a file, 
this snoop will catch it, go on and execute /usr/share/bcc/tools/opensnoop , 
and see the output.

```commandline
[root@aleivag-fedora-PC1C0JVZ workshop]# /usr/share/bcc/tools/opensnoop                                                                                                                                                                                                                                                                                                                                                   
PID    COMM               FD ERR PATH                                                                                                                                                                                                          
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                                                                                                                                                                                                   
2797   inot-hand-1       204   0 /etc/group                                                                                                                                                                                                    
2797   inot-hand-1       204   0 /etc/passwd                   
```


## other snoops to look

These programs are called snoops because Brendan Gregg worked a bunch with solaris back in the day, where the prefer name for tracers was “snoop”. you can execute 


```
[root@7ece76c6d931 workshop]# ls /usr/share/bcc/tools/*snoop 
/usr/share/bcc/tools/bindsnoop     /usr/share/bcc/tools/dcsnoop    /usr/share/bcc/tools/exitsnoop   /usr/share/bcc/tools/opensnoop  /usr/share/bcc/tools/statsnoop    /usr/share/bcc/tools/ttysnoop
/usr/share/bcc/tools/biosnoop      /usr/share/bcc/tools/drsnoop    /usr/share/bcc/tools/killsnoop   /usr/share/bcc/tools/shmsnoop   /usr/share/bcc/tools/syncsnoop
/usr/share/bcc/tools/compactsnoop  /usr/share/bcc/tools/execsnoop  /usr/share/bcc/tools/mountsnoop  /usr/share/bcc/tools/sofdsnoop  /usr/share/bcc/tools/threadsnoop
```


you'll see there is a bunch, and they “kind of” correspond to a syscall.
I say kind of because sometimes there are redundant syscalls, like open that we saw earlier.


# Using bpftrace

bpftrace is a powerful and flexible opensource tracing tool for Linux systems.
It is built on top of BPF and BCC. bpftrace simplifies the process of writing scripts 
to trace various events in the system, making it easier for administrators and 
developers to analyze and monitor system behavior in real-time.

In a way... bpftrace is like awk, in a way that is a full programing language, 
but that its most used as one liner.  

> note: The following section looks pretty similar to the [official tutorial](https://github.com/bpftrace/bpftrace/blob/master/docs/tutorial_one_liners.md) 

## listing all the probes we can trace

Same as BCC, you will ultimately end up hooking yourself to some sort of trace event, its
reasonable to ask then, "what events, probes can I hook myself". For that you can call 
`bpftrace` with the  `-l` option and some filter, for instance, if we want to know what "open" events there are
you can search for:

```
# bpftrace -l 'tracepoint:syscalls:sys_enter_open*'
tracepoint:syscalls:sys_enter_open
tracepoint:syscalls:sys_enter_open_by_handle_at
tracepoint:syscalls:sys_enter_open_tree
tracepoint:syscalls:sys_enter_openat
tracepoint:syscalls:sys_enter_openat2
```

or

```
# bpftrace -l 'tracepoint:syscalls:sys_exit_open*'
tracepoint:syscalls:sys_exit_open
tracepoint:syscalls:sys_exit_open_by_handle_at
tracepoint:syscalls:sys_exit_open_tree
tracepoint:syscalls:sys_exit_openat
tracepoint:syscalls:sys_exit_openat2
```

What is the difference between "enter" and "exit"?

* tracepoint:syscalls:sys_enter_openat2: This tracepoint captures the entry point of the openat2 system call. It provides information about the parameters passed to the system call before it is executed.
* tracepoint:syscalls:sys_exit_openat2: This tracepoint captures the exit point of the openat2 system call. It provides information about the result of the system call, including the return value.

## hello world? in bpftrace? yes please

Execute:

```
# bpftrace -e 'BEGIN { printf("hello world\n"); }'
Attaching 1 probe...
hello world
^C
```

"We did nothing, but in a way, we did a lot!"

But instead of hanging, we can 
```
# bpftrace -e 'BEGIN { printf("hello world\n"); exit() }'
Attaching 1 probe...
hello world

#
```


## tracing open files part 2

To trace all the files that are open in the system, you can do something like:

```commandline
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%-16s %-6d %s\n", comm, pid, str(args->filename)); }'
```

To filter by filename, do the same as awk, and `/str(args->filename)=="README.md"/`

```
bpftrace -e 'tracepoint:syscalls:sys_enter_openat /str(args->filename)=="README.md"/ { printf("%-16s %-6d %s\n", comm, pid, str(args->filename)); }'
```

please notice that this is when an app issue the syscall openat, does does not mean the file
exists for instance on another terminal you can

```commandline
cd $(mktemp -d)
cat README.md
ls README.md
```


And CAT will show up in the bpftrace, but not ls, 

```commandline
cat              1948158 README.md
```

This is because, cat will try to open the file, but ls does not try to open the file, but to call a statx

```
[root@aleivag-fedora-PC1C0JVZ tmp.N2rt8ef8y1]# strace -e trace=openat,statx cat README.md 2>&1 | grep README
openat(AT_FDCWD, "README.md", O_RDONLY) = -1 ENOENT (No such file or directory)

[root@aleivag-fedora-PC1C0JVZ tmp.N2rt8ef8y1]# strace -e trace=openat,statx ls README.md 2>&1 | grep README
statx(AT_FDCWD, "README.md", AT_STATX_SYNC_AS_STAT|AT_NO_AUTOMOUNT, STATX_MODE, 0x7ffe502c0a00) = -1 ENOENT (No such file or directory)
statx(AT_FDCWD, "README.md", AT_STATX_SYNC_AS_STAT|AT_SYMLINK_NOFOLLOW|AT_NO_AUTOMOUNT, STATX_MODE, 0x7ffe502c0a00) = -1 ENOENT (No such file or directory)
```

### what if we want only the succeeded reads

This is where enter and exit hook works, we will gather the fileinfo when openat is called, and will
store it using the tid (thread id), and based on that info, we will print the info, based on the return value of
openat, see

```
bpftrace -e '

    tracepoint:syscalls:sys_enter_openat /str(args->filename)=="README.md"/{  
        @filename[tid] = args.filename; 
    }
    
    tracepoint:syscalls:sys_exit_openat /@filename[tid]/{
        if (args.ret > 0){
            printf("%-16s %-6d %s\n", comm, pid, str(@filename[tid]));
        }
        delete(@filename[tid]);
    }
'
```

and execute

```commandline
cd $(mktemp -d)
cat README.md
```

You'll see no output, now do

```commandline
cd $(mktemp -d)
touch README.md
cat README.md
rm README.md
```

you'll see touch, and cat, but not rm... "how does rm work"?

```
strace rm -f  README.md 2>&1 | grep README
execve("/bin/rm", ["rm", "-f", "README.md"], 0x7ffc75ed0640 /* 25 vars */) = 0
newfstatat(AT_FDCWD, "README.md", {st_mode=S_IFREG|0644, st_size=0, ...}, AT_SYMLINK_NOFOLLOW) = 0
unlinkat(AT_FDCWD, "README.md", 0)      = 0
```

### This is getting big, can I just write scripts?

Yes the same as with awk, you can do scripts, and the same as BCC, bpftrace comes with a lot
of prebuild scripts,
that you can find in `/usr/share/bpftrace/tools/` like [/usr/share/bpftrace/tools/opensnoop.bt](https://github.com/bpftrace/bpftrace/blob/master/tools/opensnoop.bt)

In fact, most of the scripts in `/usr/share/bcc/tools` can also be found in `/usr/share/bpftrace/tools`, 
This begs the question, which one is better? The answer is neither and both... and depends.

* **bpftrace**: Is useful when you need to write a program to collect data and display it in the same process, there are no command-line arguments, so most things in bpftrace are hardcoded. On the other hand, writing a bpftrace program is simple and the language does not stand in the way of your program, making things like "attaching to multiple events" very simple.
* **bcc**: It's very powerful when you need to interact with more than just the program you are running, passing things from the kernel to your application is very simple, and then you can use your application to process even further. Since you can do whatever the language you pick can do, passing command-line applications or communicating with other processes is extremely easy. On the other hand, you have to do most of the work yourself when interacting with bpf.

from [introduction-bpftrace](https://opensource.com/article/19/8/introduction-bpftrace):

> Since eBPF has been merging in the kernel, most effort has been placed on the BCC frontend, which provides a BPF library and Python, C++, and Lua interfaces for writing programs. I've developed a lot of tools in BCC/Python; it works great, although coding in BCC is verbose. If you're hacking away at a performance issue, bpftrace is better for your one-off custom queries. If you're writing a tool with many command-line options or an agent that uses Python libraries, you'll want to consider using BCC.

> On the Netflix performance team, we use both: BCC for developing canned tools that others can easily use and for developing agents; and bpftrace for ad hoc analysis. The network engineering team has been using BCC to develop an agent for its needs. The security team is most interested in bpftrace for quick ad hoc instrumentation for detecting zero-day vulnerabilities. And I expect the developer teams will use both without knowing it, via the self-service GUIs we are building (Vector), and occasionally may SSH into an instance and run a canned tool or ad hoc bpftrace one-liner.

> ... Brendan Gregg

## Other observability tools not covered here:

* [perf(1)](https://man7.org/linux/man-pages/man1/perf.1.html): Linux profiling with perf - uncover performance bottlenecks.
* [ftrace](https://en.wikipedia.org/wiki/Ftrace): ftrace (Function Tracer) is a tracing framework for the Linux kernel. Although its original name, Function Tracer, came from ftrace's ability to record information related to various function calls performed while the kernel is running, ftrace's tracing capabilities cover a much broader range of kernel's internal operations.
* [SystemTap](https://en.wikipedia.org/wiki/SystemTap): Is a scripting language and tool for dynamically instrumenting running production Linux-based operating systems.

# Userspace Probes

We can't let the kernel have all the fun. For this Userspace Probes, also known as USDT (Userspace Statically Defined Tracing) or uprobes, exists.
They are a type of dynamic tracing tool that allows developers to insert trace points into running processes without modifying the 
kernel or recompiling the application. This makes them useful for debugging and profiling applications in production environments. 

The caveat is that application must be compiled with support for this, and they do come with "some" performance cost, 
let's explore some very simple: 

## Python Probes USDT

"system python" (a.k.a as teh python that comes with your machine) does not come with uprobes, but in this workshop we
provide a python interpreter compiled with some support, you can see the [--with-dtrace](https://github.com/systemdemo/workshop/blob/main/bin/provision-build#L161-L166)
on python ./configure

to know if a binary ahs uprobes, you can 

```commandline
[root@aleivag-fedora-PC1C0JVZ workshop]# /usr/share/bcc/tools/tplist -l /opt/cpython/bin/python3.12
/opt/cpython/bin/python3.12 python:import__find__load__start
/opt/cpython/bin/python3.12 python:import__find__load__done
/opt/cpython/bin/python3.12 python:audit
/opt/cpython/bin/python3.12 python:gc__start
/opt/cpython/bin/python3.12 python:gc__done
```

Check id /usr/bin/python has any?.  how about /usr/bin/qemu-system-x86_64?

To explore this, probes, lets start a python interpreter on another terminal


```commandline
# /opt/cpython/bin/python3.12
Python 3.12.2 (tags/v3.12.2:6abddd9f6a, Feb 29 2024, 01:33:51) [GCC 13.2.1 20231205 (Red Hat 13.2.1-6)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os           
>>> os.getpid()
353
```
now lets hook to this probes, both bcc and bpftrace has support for this, so lets  test both:

```commandline
/usr/share/bcc/tools/trace 'u:/opt/cpython/bin/python3.12:audit "%s", arg1' -p 353
```



```commandline
>>> import sys                                                                                                                                                                                                                                 
>>> sys.audit("hello") 
```

```commandline
520838  520838  python3.12      audit            hello  
```
