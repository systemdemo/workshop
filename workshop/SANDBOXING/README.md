# Sandboxing

## Mount Namespaces / Mount Isolation

Linux namespaces are a kernel feature for creating isolated environments for processes and system resources. They are widely used in container technologies to provide secure and efficient virtualization of system resources.

Mount namespaces in particular allow isolation of the file system mount points so that processes in one namespace cannot see or access files or directories in another namespace. Let's dive into some of the systemd features that make use of mount namespaces.

We've provided a service unit called `mount_ns.service`. Let's look at the contents:

```
[~] systemctl cat mount_ns.service
# /etc/systemd/system/mount_ns.service
[Service]
ProtectHome=yes
ProtectSystem=full
PrivateTmp=true
BindPaths=/usr/lib/systemd
ExecStart=sleep infinity
```

We'll be exploring a variety of mount namespacing features by spinning up a process that sleeps while we enter its namespace to run some experiments. For this portion of the workshop it will be helpful to have 2 windows or terminal panes: one that is entering the namespace of the process, and another that remains in the root namespace (i.e. outside of the process's namespace).

Let's go ahead and start the unit:

```
[~] systemctl start mount_ns.service
```

Since this unit is only running one process, we can use `systemctl show` to easily get the process ID (PID):

```
[~] systemctl show --value -p MainPID mount_ns.service
```

To enter the namespace of the process, we will be using a tool called `nsenter`. We will pass the `--target` argument to specify the target PID. In this case it is the sleep process from `mount_ns.service`. We will also be using the `--all` argument to tell `nsenter` that we will be entering all the namespaces for the target process. Hopefully you have 2 terminal panes available. Let's enter the namespaces in one terminal pane:

```
[~] nsenter --target <PID from previous command> --all
```

The first setting from the service we will explore is `ProtectHome=yes`. This will set the /home, /root, and /run/user directories to be empty and inaccessible. You can check by running `ls` both inside the service namespace, and outside of the service namespace to view the files (this is why I said to have 2 terminal panes available :)):

```
[~] ls /home /root /run/user
```

If you run `ls -l /` both inside and outside of the service's namespace, you'll notice the permissions for /home and /root are also very different (`d---------` vs. `dr-xr-x---`).

Next is `ProtectSystem=full`: This will mount the /usr and the boot loader directories (/boot and /efi) read-only; If set to "full", the /etc directory is mounted read-only, too. This property can also take the option `strict` which will mount the entire file system hierarchy read-only (except for /dev, /proc,/ and /sys). Let's test this out by trying to create files in /usr, /boot, and /etc both inside and outside of the service's namespace:

```
[~] touch /usr/meow
[~] touch /boot/meow
[~] touch /etc/meow
```

This should fail when run inside the service's namespace, but succeed when run outside.

Let's look at `PrivateTmp=true`: This mounts a new tmpfs under /tmp and /var/tmp so that files created inside are unique to the process and not visible outside of the namespace. Let's try this out by creating a file from inside the namespace and verifying that it does not exist from outside the namespace.

From inside the namespace (these commands will succeed):

```
[~] touch /tmp/alvaroandanita
[~] ls /tmp/alvaroandanita
```

From outside the namespace (this file will not exist):

```
[~] ls /tmp/alvaroandanita
```

`BindPaths=` is a way to poke holes in some of the restrictions set by other sandboxing properties by bind mounting a path from the host into the process's namespace. This will allow the process to have a connection to outside of the namespace. You can change the target destination of the mount in the process's namespace by passing a colon-separated option to the property. But in this unit, we set `BindPaths=/usr/lib/systemd` which means it will just use `/usr/lib/systemd` as both the source (from outside the namespace) and the destination (to inside the namespace). Try touching a file under this directory from inside the namespace:

```
[~] touch /usr/lib/systemd/alvaroandanita
```

Check that it appears both inside and outside the namespace:

```
[~] ls /usr/lib/systemd/alvaroandanita
```

Exit from `nsenter` and stop the service when you are done.

## Chroot

Chroot (short for "change root") is a Unix command that allows a user to change the root directory of a process or group of processes to a new location in the file system. When a process is run in a chroot environment, it can only access files and directories that are located within the new root directory. However, chroot by itself does not provide an isolated resource (like mount namespaces). Changes you make in a chroot will still show up in the original directory on the host. Let's test chroot out now:

```
[~] chroot /opt/debian
[~] cat /etc/os-release
[~] touch /meow
```

/opt/debian is the root directory of a Debian distribution we've provided for you. Looking at /etc/os-release, you can tell that from the current view of the file system it appears that you are on a Debian host! If you exit the chroot and look at /etc/os-release again you'll see that you're back in the view of a Fedora host:

```
[~] exit
[~] cat /etc/os-release
```

What about the file /meow that we created? You will find it in the original (outside of the chroot) directory, /opt/debian/meow:

```
[~] ls /opt/debian/meow
```

However, just calling chroot by itself has limitations. For example, procfs is not available:

```
[~] chroot /opt/debian
[~] cat /proc/1/cmdline
[~] exit
```

Next we'll see how systemd makes this functional. We've provided a systemd service called `chroot.service` that uses `RootDirectory=` to mimic the same behavior we just tested with `chroot`:

```
[~] systemctl cat chroot
# /etc/systemd/system/chroot.service
[Service]
RootDirectory=/opt/debian
MountAPIVFS=true
ExecStart=sleep infinity
```

`MountAPIVFS=true` is the magic property that will make procfs and other features work. By setting it to true, /proc/, /sys/, /dev/ and /run/ (as an empty "tmpfs") are mounted inside of it. Let's do what we did in the previous section: start the service and enter the sleep process's namespace. Then run some experiments as we did when running inside `chroot`:

```
[~] systemctl start chroot
[~] nsenter -t $(systemctl show --value -p MainPID chroot.service) --all
[~] touch /alvaroandanita
[~] cat /proc/1/cmdline
```

This time you should be able to `cat` /proc/1/cmdline. From outside the chroot you should see /opt/debian/alvaroandanita.

## Dynamic Users

Sometimes you don't care which user your unit's processes should run as, as long as it is not root. There is the `User=` property available, but the problem is you need the user provided to exist on the system. Systemd provides a novel property called `DynamicUser=` which will create users on-demand when a service is started and destroy then when the service stops. This is in contrast to system users, which are created during installation or configuration and persist even when the associated service is not running. The UID is allocated from a range set by systemd. You can read more about them in the [documentation](https://systemd.io/UIDS-GIDS/).

When the unit stops, all the files and state associated with that user are cleaned up. Systemd does this using mount namespaces, which means using `DynamicUser=` also implicitly enables `ProtectSystem=strict` and `ProtectHome=read-only` (properties we've seen above) along with a bunch of other properties to privatize the state.

We've provided a service unit called `dynamic_user.service`. Let's look at the contents:

```
[~]# systemctl cat dynamic_user
# /etc/systemd/system/dynamic_user.service
[Service]
DynamicUser=yes
ExecStart=sleep infinity
```

Start the service and get the PID:

```
[~] systemctl start dynamic_user
[~] systemctl show --value -p MainPID dynamic_user
```

We can get the user of the running process in this service by using the `ps` command:

```
[~] ps -p <PID output by the previous command> -o user,uid,pid,command,cgroup
```

This command shows the name of the user running the PID, the UID, the PID, the command, and the cgroup associated. Notice that the user is not root, but should also not be any user that exists permanently on the system.

Stop the service when you are done.

## Network Isolation

Isolating processes from the network is also a common feature of containerization solutions. We'll talk about 2 different ways to do this.

The first is `PrivateNetwork=true` which makes use of network namespaces. This sets up a new network namespace for the executed processes and configures only the loopback network device "lo" inside it. For this example we will use `systemd-run` (just to switch it up). Because it uses Linux namespaces, you can still use `nsenter` as in the mount namespace example. But by using `systemd-run` to start a shell and connect a pseudo-terminal, your shell will automatically inherit the namespaces from the first process of the unit so you can run commands from the command line inside the namespaces.

Let's try it:

```
[~] systemd-run --pty -p PrivateNetwork=true /bin/bash
```

Once this successfully runs you will be in a shell that has inherited the namespace setup. You can check that only the "lo" interface is available by running `ip address` to show the interfaces and addresses:

```
[~] ip address
```

You can check that network is not available by running `ping` from within the namespace:

```
[~] ping -c 1 8.8.8.8
```

Exit from the `systemd-run` shell when you are done.

You'll notice that `PrivateNetwork=` is all or nothing. The other way to isolate the network is to use `IPAddressDeny=` and `IPAddressAllow=`. This allows more controlled network isolation by using eBPF to filter at the socket level. It does not use network namespaces (and so `nsenter` will not work to test this).

Let's try the previous commands, but now with 8.8.8.8 denied:
```
[~] systemd-run --pty -p IPAddressDeny=8.8.8.8 /bin/bash
[~] ip address
[~] ping -c 1 8.8.8.8
```

You can see that we still have interfaces other than "lo" set up. If you try to ping a different address it should still work:
```
[~] ping -c 1 8.8.4.4
```

Exit from the `systemd-run` shell when you are done.
