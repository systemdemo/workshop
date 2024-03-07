
Now we are going to talk about a topic that is not really systemd related, but we think it's interesting to talk about
nevertheless, and we do this tutorial to have fun,and talk about fun stuff.

The topic it’s titled “Extended Berkeley Packet Filter”, but you might have heard of it as eBPF (or just BPF, because lets
be honest, no one talks about BPF anymore).
If you work in the system space and you haven't heard of it, talk to us, as we wanna know how it feels to live under a
rock for the last 10 years.

Jokes aside, eBPF is perhaps one of the hottest topics that comes out in conversation about systems profiling, management
and systems in general.


# What is eBPF.

eBPF is a powerful and flexible technology that allows you to write custom code that can be attached to various points
in the Linux kernel, _without needing to recompile the kernel itself_. It's the successor of BPF (Berkeley Packet Filter,
originally developed in 1992 in… well berkley) because it extends its capabilities and design (hence the name).

In simpler terms, you write a program, compile it, and then you ask the kernel to run it for you. Does this sound familiar?
There is another very famous programming language that people write, that reacts and interacts with a “bigger machine”
without needing to recompile this machine, and that's javascript. In many ways, eBPF is the javascript of the kernel.

One last thing to say before we dive into eBPF, is  that the world of eBPF seems to be divided in 2 groups of people,
1) people who have never heard of it, or have but are not clear on what it is, and
2) people who use eBPF to do very complex things, and very vocal about it, giving the impression to the first group that
eBPF is hard.

Well here we aim to show you all  that even though you can do complex things, it’s very easy to  get started.

If you would like to know more about the history of eBPF there is [a fun documentary](https://youtu.be/Wb_vD3XZYOA?si=RRxG_rUwXxTf2xnh)
about it, that even have Brendan Gregg saying "this is like putting javascript into the kernel".

# Kernel space/User space and syscalls.

Before we start talking about eBPF, let's recap what userspace and kernel space. In layman terms, linux execution is
divided into 2 big areas,  Kernel Space, that is where all the kernel related processes are executed, and userspace,
that is everything else. This means that everything that is related to the operative system is completely isolated from
things a user might run. This distinction exists for 3 reasons:

1. Security:
    1. Keeping the kernel and user space separate enhances system security. If a user program were to directly access kernel space, it could potentially compromise the entire system.
    2. By isolating the kernel in its own protected space, unauthorized access and tampering are minimized.
2. Stability:
    3. The kernel is critical for the proper functioning of the operating system. Isolating it in its own space helps prevent user applications from causing unintended interference or crashes in the kernel.
    4. If a user program crashes, it typically does not affect the kernel, allowing the system to remain stable.
3. Efficiency:
    5. Separating user space and kernel space allows the kernel to have direct access to hardware resources, enabling efficient system-level operations.
    6. User programs can run in their own space without requiring direct hardware access. They communicate with the kernel through system calls, allowing the kernel to manage hardware resources on their behalf.

When the user needs to do something that only the kernel can do (e.g. write a file to disk), the user will call a “system call” or just syscall, this function is a safe boundary between these 2 spaces.


## Seeing syscall in actions: how does the os write a file to disk.

A classical interview question is “how does the os do’ something’ ”, one that used to like asking was “once you hit save on your text editor of choice… what happens”. I don’t ask that question anymore, but the idea it's super interesting to understand the difference between userspace and kernel space. let's take the simple script we have:


```
root@c8c835070254 workshop]# cat ./eBPF/write-to-disk.py
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
```


This script is super simple, at its core it “store the a filename into a variable, then open that file, write to that file, flush the buffer, and close the file”, between this steps we write some flags, to help us navigate the output and know what lines execute what syscalls.

Lets execute the file using strace, but let’s use tmux so we can navigate the output better


```
tmux
strace -o /tmp/strace.out python3 ./eBPF/write-to-disk.py
```


This stored the syscalls that `python3 ./eBPF/write-to-disk.py`, done in the file /tmp/strace.out . you can inspect that file using vim, you can use your editor of choice, but here we will give vim instructions

open the file with
```
[root@c8c835070254 workshop]# vim /tmp/strace.out
```
Then  type “/MYVAR” and press enter. this will take you to a line that looks like `write(1, "MYFLAG\n", 7)                 = 7` this line corresponds to the line `print("MYFLAG")` on the file we used. This line serves no purpose other than mark where, in all the call stack, we want to start paying attention.

the next 3 lines looks like

```python
write(1, "##########\n", 11)            = 11
write(1, "########## GOING TO ASIGN A VARI"..., 37) = 37
write(1, "\n", 1)                       = 1
```

those clearly correspond to

```python
print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO ASIGN A VARIABLE")
filename = "/tmp/not-exists"
print()
```

But, wait a minute!, in the list of syscalls there are 3 calls to write to file descriptor 1, those are clearly the print statement, but there is nothing to indicate that a variable was assigned. This is how python works, python manages the memory for you, mostly in userspace, (one of the reasons it's so damn hard to debug memory leaks in python. If for some reason you would need to actually allocate memory (because you run out), then you would see something like `mmap(NULL, 1052672, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fa28d628000` (probably its worth showing an example).

moving along the next lines we see are:


```
write(1, "##########\n", 11)            = 11
write(1, "########## GOING TO open /tmp/no"..., 41) = 41
openat(AT_FDCWD, "/tmp/not-exists", O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC, 0666) = 3
newfstatat(3, "", {st_mode=S_IFREG|0644, st_size=0, ...}, AT_EMPTY_PATH) = 0
ioctl(3, TCGETS, 0x7ffd82a21880)        = -1 ENOTTY (Inappropriate ioctl for device)
lseek(3, 0, SEEK_CUR)                   = 0
lseek(3, 0, SEEK_CUR)                   = 0
write(1, "\n", 1)                       = 1
```


that correspond to

```python
print(f"{LOGGING_PREFIX}")
print(f"{LOGGING_PREFIX} GOING TO open {filename}")
file_= open(filename, "w")
print()
```

This time is different, between the last 2 writes to file descriptor 1, we see 4 syscalls been executed:


1. openat, responsible for opening the file, in the correct mode
2. newfstatat: it's the modern equivalent of stat
3. ioctl: that fails, but its used to gather information about the terminal
4. two calls to lseek to polace the pointer to the beginning of the file… why 2? i don’t know.

This is interesting, because a single call in userspace triggered a bunch of calls in the kernel. Let's see what writing actually does!!

```
write(1, "##########\n", 11)            = 11
write(1, "########## GOING TO write TO /tm"..., 45) = 45
write(1, "\n", 1)
```


oh no, between `write(1, "########## GOING TO write TO /tm"..., 45) = 45` and `write(1, "\n", 1)`, we were expecting a write syscall. well python didn’t issue one, because it buffered the content into memory. The writing will happen in one of the following situations

1. The file is closing (a normal python exit will also close the file and flush the contents).
2. the buffer get full,
3. an explicit call to flush.

So lets see the next lines


```
write(1, "##########\n", 11)            = 11
write(1, "########## GOING TO flush /tmp/n"..., 42) = 42
write(3, "42", 2)                       = 2
write(1, "\n", 1)
```


we now see a ``write(3, "42", 2)`` between the last 2 write to fd 1, that was triggered by our flush. finally we close the the file with


```
write(1, "##########\n", 11)            = 11
write(1, "########## GOING TO close /tmp/n"..., 42) = 42
close(3)                                = 0
write(1, "\n", 1)
```


exercise for the reader, We saw that calling write in python did not translate into a write syscall, why? Is this python, or is there something else going on? How can we know?. see the strace output (the last 10 lines ) of  write-to-disk-force-close.py and write-to-disk-unforce-close.py.

---
[back to TOC](../README.md)
