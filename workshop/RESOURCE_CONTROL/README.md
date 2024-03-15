# Cgroup Fundamentals

## What are cgroups

Control groups (more commonly known as cgroups), are a Linux kernel feature that allows you to manage, restrict, and audit groups of processes. It's one of the most fundamental features in modern day Linux, essential for use in containerization and of course, systemd. The basis of systemd service management lies in its use of cgroups: the majority of units have an associated cgroup which systemd uses to organize/groups units. For the purpose of this workshop, we will only refer to the cgroups v2 implementation of cgroups; cgroups v1 is beginning to get phased out in newer versions of systemd and many distributions are cgroups v2 by default.

So what exactly is cgroups2? It is a virtual file system mounted by default at `/sys/fs/cgroup`. It is nothing more than a tree of files and directories. If you try to create a new cgroup, it will get automatically populated with the files provided by the Linux kernel. Let's try it:
```
[~] mkdir /sys/fs/cgroup/foreignunit
[~] ls /sys/fs/cgroup/foreignunit
```
You should see there are many files prefixed with CPU, IO, and memory which control the knobs for resource control. CPU, IO, and memory are examples of "controllers" that you can enable or disable for resource control. How do you know which controllers are enabled on the cgroup? By examining `cgroup.controllers`:

```
[~] ls /sys/fs/cgroup/foreignunit/cgroup.controllers
```

Now let's make another cgroup under `/sys/fs/cgroup/foreignunit` and examine the contents:
```
[~] mkdir /sys/fs/cgroup/foreignunit/anotherforeignunit
[~] ls /sys/fs/cgroup/foreignunit/anotherforeignunit
```

You should see that the controller files are not there. And if you peek into `/sys/fs/cgroup/foreignunit/anotherforeignunit/cgroup.controllers`, you will see the file is empty. Why? In order the enable/disable controllers for your cgroup, you need to go to your parent cgroup and modify `cgroup.subtree_control`. This file dictates which controllers will be available in all the children. Let's try to enable the memory controller for /sys/fs/cgroup/foreignunit/anotherforeignunit:

```
[~] cat /sys/fs/cgroup/foreignunit/anotherforeignunit/cgroup.controllers # this is currently empty
[~] cat /sys/fs/cgroup/foreignunit/cgroup.subtree_control # this is currently empty
[~] echo "+memory" > /sys/fs/cgroup/foreignunit/cgroup.subtree_control
[~] cat /sys/fs/cgroup/foreignunit/cgroup.subtree_control
[~] cat /sys/fs/cgroup/foreignunit/anotherforeignunit/cgroup.controllers
[~] ls /sys/fs/cgroup/foreignunit/anotherforeignunit
```

Now you will see all the memory-related resource control files appear under `/sys/fs/cgroup/foreignunit/anotherforeignunit`.

## systemd and cgroups

Writing directly to arbitrary parts of the cgroups2 tree, as we did in the previous example, violates one of the contracts with systemd: unless otherwise delegated there should only be one writer to the cgroup2 tree. In the previous example, we enabled a controller by writing directly to the cgroup files. systemd is creating cgroups every time it is spinning up a new service, scope, and slice unit. And as part of that process systemd also needs to modify cgroup files according the properties you set. If there are multiple writers on the cgroups2 tree, you can imagine that there can be some really troublesome race conditions when it comes to managing resource control.

So how do we tell systemd we want control over our own cgroup? You use the `Delegate=` property which is available in service and scope unit types. What this does it tell systemd which controllers you want to enable, and also that you will be modifying cgroups under the croup/unit it is going to create for you. Let's try this out:

```
[~] systemd-run --unit myfirstcgroup -p Delegate=yes sleep infinity
[~] systemctl status myfirstcgroup.service
[~] systemctl cat myfirstcgroup.service
```

The systemctl status command will show you a field called "Cgroup" which is relative to the root cgroup. The root cgroup is at /sys/fs/cgroup and it's usually dropped for brevity.

The systemctl cat command will show you where the `Delegate=yes` is set on the unit file. It is under the `[Service]` header.

Remember how in the previous example, when we made anotherforeignunit under foreignunit there were no resource control files? Since we told systemd to enable all the controllers with `Delegate=yes`, we should see all the controllers available in myfirstscope.service's cgroup:

```
[~] cat /sys/fs/cgroup/system.slice/myfirstcgroup.service/cgroup.controllers
[~] ls /sys/fs/cgroup/system.slice/myfirstcgroup.service
```

Now we can create and modify cgroups under /sys/fs/cgroup/system.slice/myfirstcgroup.service without violating systemd's single writer contract!

```
mkdir /sys/fs/cgroup/system.slice/myfirstcgroup.service/pewpew
```

Functionally nothing changes here since systemd doesn't stop you from writing to abitrary cgroups without using `Delegate=`. However I can guarantee that if you didn't follow the contract, somewhere in the future it will bite you.

The other thing systemd uses cgroups for is managing processes. There is a rule in cgroups2 that you can only have processes in the leaf cgroup nodes (cgroups without children cgroups). The kernel prevents you from modifying a cgroup subtree unless this is followed. Let's try it out using the cgroup we just made:

```
echo "+memory" > /sys/fs/cgroup/system.slice/myfirstcgroup.service/cgroup.subtree_control
```

You should see "write error: Device or resource busy". You can tell if there is a process in the cgroup by looking at cgroup.procs:

```
cat /sys/fs/cgroup/system.slice/myfirstcgroup.service/cgroup.procs
```

This shows all the PIDs running under that cgroup. You can move it to the child cgroup by writing the PIDS to pewpew's cgroup.procs file:

```
[~]# echo <PID from previous output> > /sys/fs/cgroup/system.slice/myfirstcgroup.service/pewpew/cgroup.procs
[~]# cat /sys/fs/cgroup/system.slice/myfirstcgroup.service/cgroup.procs
[~]# cat /sys/fs/cgroup/system.slice/myfirstcgroup.service/pewpew/cgroup.procs
```

Now if you try to enable the memory controller for pewpew it will work:

```
echo "+memory" > /sys/fs/cgroup/system.slice/myfirstcgroup.service/cgroup.subtree_control
```

## Resource Control

The phrase "resource control" has been used throughout this chapter, but what does it mean? When we talk about "resource control" we are talking about certain "resources", like memory, IO, CPU, etc., that we can use to "control" the limits on the system. For example, the amount of memory a cgroup uses, how much CPU time a unit should get, etc. Memory management is relatively easy to observe, so let's run an experiment!

Let's create an ephemeral slice using systemd-run:
```
systemd-run --slice tester -u sleepyservice sleep infinity
```
We use the sleep process to keep the slice alive. If you're using tmux or screen, split your terminal in two. One on side we will watch the memory growth and the other side we will run commands. To watch the memory growth of the units under tester.slice, run:
```
systemd-cgtop tester.slice
```

Now we'll make another unit under tester.slice:
> Question: what do you think this command does?
```
systemd-run --slice tester -p MemoryMax=50% tail /dev/zero
```

There are multiple other resource control settings supported by systemd. You can see them all at the man page for [systemd.resource-control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html). For the most part, these properties are just writing directly to the cgroup files and the kernel does the rest.

## Slices

Slice unit types exist to organize cgroups in the tree. Think of how target units are used to synchronize different units, slices exist to organize units. What kind of organization? Let's look at some of systemd's slices for inspiration:

```
systemd-cgls
```

This shows you the cgroup tree for the host and all the processes running. Running it without arguments is equivalent to passing / (for root cgroup, i.e. `systemd-cgls /`). You will see that there is a user.slice, system.slice, and init.scope directly under the root cgroup.

- user.slice contains all the processes and units related to a systemd user manager. We've only used the system manager so far (PID 1). But it is possible to have multiple systemd processes running as different users.
- system.slice is the "default" cgroup and all system services (created by PID 1) are started here unless otherwise changed (via unit properties).

> Question: What are some real life examples of where you might use slices?

---
[back to TOC](../README.md)
