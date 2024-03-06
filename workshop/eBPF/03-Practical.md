In this section, we will create an eBPF program that performs actions.

---

### bpftrace: Capture all successful open files in a process and all their children.

We have done something similar before in the previous section, so we are not starting from scratch; we already have some knowledge. We will write this in a file. Either open a new shell or create a tmux terminal with two panels (`tmux` then `ctl-B %`), get the pid of one terminal by `echo $$`, for this exercise let's assume the pid was 5378.

Create a file with the following content (or check [01-openfiles.bt](samples/01-openfiles.bt)):
```c
#!/usr/bin/env bpftrace
BEGIN {
    printf("starting to monitor files for ppid %d\n", $1);
    @exectree[$1] = 1;
}
```
Execute it like this:
```bash
/usr/local/src/workshop/workshop/eBPF/samples/01-openfiles.bt 5378
...
Attaching 1 probe...
starting to monitor files for ppid 5378
^C
@exectree[5378]: 1
```
You see a few things happening here:

1. We can pass parameters with `$1...$n`; this way, we can pass the pid we want to monitor.
2. We print the pid and also add it to the global map variable `@exectree`; variables with `@` are global, while those with `$` are local, and variables with `[]` are maps.
3. We execute something at the beginning with the `BEGIN` block, causing the app to freeze.
4. We exit with `^C`, and bpftrace prints the variable we created, which is still in memory.

Now let's do some more interesting things. Let's track all processes created by adding the following code (check [02-openfiles.bt](samples/02-openfiles.bt) for the full file):
```csharp
tracepoint:syscalls:sys_exit_clone /@exectree[pid]/ {
    if (args.ret > 0){
        printf("new process forked with pid %d\n", args.ret);
        @exectree[args.ret] = 1;
    }
    if (args.ret == 0) {
        printf("i'm a new process with pid %d\n", pid);
    }
}
```
Execute it and go to your shell to execute a few commands:
```bash
[root@eth50-1 workshop]# /usr/local/src/workshop/workshop/eBPF/samples/02-openfiles.bt 5378
new process forked with pid 5585
i'm a new process with pid 5585
new process forked with pid 5586
i'm a new process with pid 5586
new process forked with pid 5587
i'm a new process with pid 5587
new process forked with pid 5589
i'm a new process with pid 5589
new process forked with pid 5590
i'm a new process with pid 5590
```
Then hit `ctl+^c` and see the variables we created:
```bash
...
i'm a new process with pid 5590
^C
@exectree[5378]: 1
@exectree[5586]: 1
@exectree[5585]: 1
@exectree[5589]: 1
@exectree[5590]: 1
@exectree[5587]: 1
```
You can see that we can track clone, and a few important things here are:

1. We track clone by hooking ourselves to `tracepoint:syscalls:sys_exit_clone`.
2. We only do this for processes that have a value in `@exectree`, since in `BEGIN` we added the parent pid; thus, we have no problem keeping track of their children.
3. If clone returns a number greater than zero, then that's the pid of the child process. We add it to `@exectree` to keep track of the children of this child.
4. Clone can return zero; in that case, this is the child process. We just log it to show, but we will discard it later.
5. With `ctl+^c`, you can see that we keep the values of these children in memory.

Clean up children when they exit, see [03-openfiles.bt](samples/03-openfiles.bt):

```css
tracepoint:syscalls:sys_enter_exit_group /@exectree[pid]/ {
    delete(@exectree[pid]);
}
```

Now let's keep track of open files, similar to what we did before (see [04-openfiles.bt](samples/04-openfiles.bt)):
```csharp
tracepoint:syscalls:sys_enter_openat /@exectree[pid]/{
    @filename[tid] = args.filename;
}
tracepoint:syscalls:sys_exit_openat /@filename[tid]/{
    if (args.ret > 0){
        printf("%s\n", str(@filename[tid]));
    }
    delete(@filename[tid]);
}
```
Execute it and in the terminal run something like `python -c '1==1'`:
```bash
[root@eth50-1 workshop]# /usr/local/src/workshop/workshop/eBPF/samples/04-openfiles.bt 5378                                                                                                                                    19:31:37 [5/563]
Attaching 5 probes...                                                                                                                                                                                                                          
...
/usr/lib64/python3.12/encodings/__pycache__/__init__.cpython-31..
/usr/lib64/python3.12/encodings
/usr/lib64/python3.12/encodings/__pycache__/aliases.cpython-312..
/usr/lib64/python3.12/encodings/__pycache__/utf_8.cpython-312.p..
/usr/local/lib64/python3.12/site-packages
/usr/local/lib/python3.12/site-packages
/usr/lib64/python3.12/site-packages
/usr/lib/python3.12/site-packages
```
It's working, but the output is truncated!!! This is because bpftrace limits the size of strings, but we can change that with:
```bash
[root@eth50-1 workshop]# BPFTRACE_MAX_STRLEN=128 /usr/local/src/workshop/workshop/eBPF/samples/04-openfiles.bt 5378                                                                                                                            
Attaching 5 probes...                                                                                                                                                                                                                          
/etc/ld.so.cache                                                                                                                                                                                                                               
...
/usr/lib64/python3.12/encodings/__pycache__/__init__.cpython-312.pyc
/usr/lib64/python3.12/encodings
/usr/lib64/python3.12/encodings/__pycache__/aliases.cpython-312.pyc
/usr/lib64/python3.12/encodings/__pycache__/utf_8.cpython-312.pyc
/usr/local/lib64/python3.12/site-packages
/usr/local/lib/python3.12/site-packages
```
Now it's working... The relevant sections that we have not covered before are:

1. We hook to `tracepoint:syscalls:sys_enter_openat` and filter by only processes we have seen with `/@exectree[pid]/`.
2. We record the name of the file and assign it to `@filename[tid]` where tid is the thread id; we use tid instead of pid to avoid collisions with concurrency.
3. Then we attach to the exit event of open with `tracepoint:syscalls:sys_exit_openat`, but only for threads that have open files `/@filename[tid]/`.
4. If the return value is greater than zero, it means the open succeeded, so we print the file and remove it from the map.

Finally, let's clean up and put all together in [openfiles.bt](samples/openfiles.bt):
```csharp
#!/usr/bin/env bpftrace
BEGIN {
    @exectree[$1] = 1;
    // we don't have to define "first_clone", but why not?
    @first_clone;
}
END {
    clear(@exectree);
}
tracepoint:syscalls:sys_exit_clone /@exectree[pid]/ {
    if (args.ret > 0){
        @exectree[args.ret] = 1;
    }
    if (!@first_clone) {
        @first_clone = args.ret;
    }
}
tracepoint:syscalls:sys_enter_exit_group /@exectree[pid]/ {
    delete(@exectree[pid]);
    if (@first_clone == pid) {
        delete(@first_clone);
        delete(@exectree[20020]);
        exit();
    }
}
tracepoint:syscalls:sys_enter_openat /@exectree[pid]/{
    @filename[tid] = args.filename;
}
tracepoint:syscalls:sys_exit_openat /@filename[tid]/{
    if (args.ret > 0){
        printf("%s\n", str(@filename[tid]));
    }
    delete(@filename[tid]);
}
```
Note on bugs, or don't sue us if this does not work on your system...

1. You can clone and never exit; signals and other things can influence this.