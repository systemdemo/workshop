
Now that we have a good understanding of what syscalls are, and how to monitor them, it's time to dive a bit more in the world of eBPF.

eBPF can be used  for networking, observability and security, we will focus mostly on observability.

In this section we will not dive much into the in and out, but we will explore a couple of tools that come with bcc-tools. A few caveats before we start. 



1. If you are running this inside a container, there are chances that this will not work, or… will not work as expected, containers and kernel space have a very rocky relationship, so for this section if you do it on a vm, it will probably work.
2. This will definitely not work on vanilla podman on macos and windows, as the vm image used for this is super lock down. we prefer vm for this on this OS, which means that m1/m2 users are out.

Ok, let's get started…


# Exploring bcc-tools

/usr/share/bcc/tools/ is full of a bunch of useful scripts that you can use in your analysis, but the best thing about them is that they are all written in python and are very simple to understand… You can use them as learning materials. lets see a couple

execsnoop

perhaps the most famous just run:


```
[root@7ece76c6d931 workshop]# /usr/share/bcc/tools/execsnoop 
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


a bunch of  garbage to stderr/out from compiling something, (no worries we will understand that part later), and then the actual output 


```
PCOMM            PID     PPID    RET ARGS                                                                                                                                                                                                      
solo_collector   1214474 1         0 /opt/chef-solo/bin/solo_collector --bundle_name cpe_init --verbose                                                                                                                                                                                                                                                           
systemd-userwor  1214496 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
systemd-userwor  1214495 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
systemd-userwor  1214497 1208832   0 /usr/lib/systemd/systemd-userwork xxxxxxxxxxxxxxxx                                                                                                                                                        
git              1214529 1052931   0 /usr/share/gitkraken/resources/app.asar.unpacked/git/bin/git -c gpg.format=openpgp -c tag.gpgSign=0 -c commit.gpgSign=0 -c fetch.prune=1 -c gpg.program=gpg -c credential.helper= -c safe.directory=* -c g
c.auto=0 -c gpg.ssh.program=ssh-keygen -c                                                                                                                                                                     
```


This app, monitor all the execs that happen on your system, there is no “sampling here”, so everything that get executed will show up here, go on, open a new terminal and execute something like “ls -ll” and see the line that pops up is  


```
ls               1214798 1210099   0 /bin/ls --color=auto -ll
```


Super interesting to see what is going on.

You can see the code by inspecting /usr/share/bcc/tools/execsnoop, but we live in the 21th century and we can see it in github [here](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py) . We can inspect relevant parts are, the [c eBPF code](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py#L116-L235) and the [python userspace code](https://github.com/iovisor/bcc/blob/699cd5f695b815e6e02ae92a4deed8c7ca23a2b6/tools/execsnoop.py#L305-L344) .


## other snoops to look

These programs are called snoops because Brendan Gregg worked a bunch with solaris back in the day, where the prefere name for tracers was “snoop”. you can execute 

 


```
[root@7ece76c6d931 workshop]# ls /usr/share/bcc/tools/*snoop 
/usr/share/bcc/tools/bindsnoop     /usr/share/bcc/tools/dcsnoop    /usr/share/bcc/tools/exitsnoop   /usr/share/bcc/tools/opensnoop  /usr/share/bcc/tools/statsnoop    /usr/share/bcc/tools/ttysnoop
/usr/share/bcc/tools/biosnoop      /usr/share/bcc/tools/drsnoop    /usr/share/bcc/tools/killsnoop   /usr/share/bcc/tools/shmsnoop   /usr/share/bcc/tools/syncsnoop
/usr/share/bcc/tools/compactsnoop  /usr/share/bcc/tools/execsnoop  /usr/share/bcc/tools/mountsnoop  /usr/share/bcc/tools/sofdsnoop  /usr/share/bcc/tools/threadsnoop
```


you see there is a bunch, and they “kind of” correspond to a syscall. I say kind of because sometime there are redundant syscalls , let's take opensnoop

There are 3 ways of opening a file ([`open`](https://man7.org/linux/man-pages/man2/open.2.html), [`openat`](https://man7.org/linux/man-pages/man2/open.2.html) and [`openat2`](https://man7.org/linux/man-pages/man2/openat2.2.html)… yes deprecating things is hard).  opensnoop monitors all 3, so no matter how a process wants to open a file, this snoop will catch it, go on and execute /usr/share/bcc/tools/opensnoop , and see the output.
