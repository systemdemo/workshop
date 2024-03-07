
# Using `systemd-analyze security` to restrict an nginx instance.

In this exercise, we will explore how to configure and restrict an nginx service that is running as a file server under systemd.

## General Overview of the Security Feature

Run `systemd-analyze security` to get the general security analysis.

```
[root@eth50-1 ~]# systemd-analyze security
UNIT                                 EXPOSURE PREDICATE HAPPY
NetworkManager.service                    7.8 EXPOSED   🙁
archlinux-keyring-wkd-sync.service        2.0 OK        🙂
auditd.service                            8.7 EXPOSED   🙁
chronyd.service                           3.9 OK        🙂
dbus-broker.service                       8.7 EXPOSED   🙁
emergency.service                         9.5 UNSAFE    😨
getty@tty1.service                        9.6 UNSAFE    😨
mdmonitor.service                         9.6 UNSAFE    😨
nginx.service                             9.2 UNSAFE    😨
pcscd.service                             9.6 UNSAFE    😨
rc-local.service                          9.6 UNSAFE    😨
rescue.service                            9.5 UNSAFE    😨
sshd.service                              9.6 UNSAFE    😨
sssd-kcm.service                          7.7 EXPOSED   🙁
sssd.service                              8.3 EXPOSED   🙁
systemd-ask-password-console.service      9.4 UNSAFE    😨
systemd-ask-password-wall.service         9.4 UNSAFE    😨
systemd-initctl.service                   9.4 UNSAFE    😨
systemd-journald.service                  4.3 OK        🙂
systemd-logind.service                    2.8 OK        🙂
systemd-oomd.service                      1.8 OK        🙂
systemd-resolved.service                  2.1 OK        🙂
systemd-timesyncd.service                 2.1 OK        🙂
systemd-udevd.service                     6.9 MEDIUM    😐
systemd-userdbd.service                   2.2 OK        🙂
udisks2.service                           9.6 UNSAFE    😨
user@1000.service                         9.4 UNSAFE    😨
vboxadd-service.service                   9.6 UNSAFE    😨
```

The service we care about its nginx.service that has an exposure score of 9.2.


## Get nginx.service Details

```
[root@eth50-1 ~]# systemd-analyze security nginx
...
[root@eth50-1 ~]# systemd-analyze security nginx
  NAME                                                        DESCRIPTION                                                             EXPOSURE
...
✗ User=/DynamicUser=                                          Service runs as root user                                                    0.4
...
→ Overall exposure level for nginx.service: 9.2 UNSAFE 😨

```

that will display all the bits that are considered insecure.


## Before We Start

Let's do a ridiculous amount of locking down, but first... let’s start nginx, to see that it fails to start by a technicality.

```
[root@eth50-1 ~]# systemctl start nginx
Job for nginx.service failed because the control process exited with error code.
See "systemctl status nginx.service" and "journalctl -xeu nginx.service" for details.
```


Running `journalctl -xeu nginx.service` shows

```
Feb 20 20:00:11 eth50-1.rsw1ah.30.frc4.tfbnw.net nginx[4778]: 2023/02/20 20:00:11 [emerg] 4778#4778: open() "/var/log/nginx/error.log" failed (2: No such file or directory)
```

Well boo-freaking-hoo, in reality we shouldn't need log files, we could just send information to the journal. But in reality, nginx has the path `/var/log/nginx/error.log` semi-hardcoded (it could be changed using the -e option at nginx start, but it has to be a file), even before reading its config file it needs to have an error log, so let’s do 2 things.

1. Let’s change all logging within nginx to be pointing to the journal.
2. Lets have systemd create the nginx directory for us.

First backup the original config with:

```
[~] cp /etc/nginx/nginx.conf{,.bkp}
```

And now lets edit nginx config file located in `/etc/nginx/nginx.conf` to modify both `error_logs` and `access_logs` to just send stuff to the journal, like:

```
...
  7 error_log syslog:server=unix:/dev/log;
  ...

 17 http {
...

 22     access_log  syslog:server=unix:/dev/log  main;
 ...
```

And let’s do the first edit to the file:

```ini
[~] systemctl edit nginx
...
[Service]
LogsDirectory=nginx
```

Let’s start nginx now and test port 80:

```
[root@eth50-1 ~]# systemctl start nginx
[root@eth50-1 ~]# curl  -sI localhost:80  > /dev/null && echo OK || echo KO
OK
```

> Note: on another panel you can do journalctl -f u nginx to follow the data, you can even see the access and error logs.


## Adding Overrides to nginx

First let's get out of the way the simplest settings:

1. Chances are that you don't need to read home directories at all.
2. We can assure that we won't change cgroups, modify kernel modules/tunables/logs.
3. We can assume that things like devices (things under /dev) can remain private
4. Already set in the parent unit, but let's also assume that we can use [`PrivateTmp=`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#PrivateTmp=)


```
[~] systemctl edit nginx
```

Add these lines:

```ini
[Service]

PrivateDevices=true
PrivateTmp=true
ProtectHome=true
ProtectControlGroups=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
```

Lets restart nginx and hit port 80:

```
[root@eth50-1 ~]# systemctl restart nginx
[root@eth50-1 ~]# curl -sI localhost
```

You can run `systemd-analyze security nginx` and check that the exposure score is now 7.4:

```
[root@eth50-1 ~]# systemd-analyze security nginx
...
→ Overall exposure level for nginx.service: 7.4 MEDIUM 😐
```

You can also see that some implicit settings have been turned on (or off depending on the point of view), things like `CapabilityBoundingSet=~CAP_SYS_MODULE` are now set.


## Now for the Fun Ones

Nginx starts as root and then sets the UID to the user nginx. It does this because it needs to listen to port 80 that's protected... Let's use socket activation to let systemd listen to port 80, and configure nginx to just use the port given to it.

### Question: is there already an `nginx.socket` configured?
>    Possible ways to see if there is a unit configured `systemctl status nginx.socket`

## Editing (creating) a non-existing unit file.

Go ahead and try `systemctl edit nginx.socket` and you'll see an error message:

```
No files found for nginx.socket.
Run 'systemctl edit --force --full nginx.socket' to create a new unit.
```

Good, it tells you what to do: run `systemctl edit --force --full nginx.socket` to force (`--force`) systemd to create a new unit file (using `--full` does not create an override) for the nginx.socket.

```
[Unit]
Description=Nginx Socket
After=network.target

[Socket]
ListenStream=80
```

Note: we will make this a bit more robust in a second.

Now we can edit the override for the nginx service file to add two extra lines:

```ini
[~/] systemctl edit nginx.service

[Unit]
After=nginx.socket
Requires=nginx.socket


[Service]
# ...
Type=simple
PIDFile=
Environment=NGINX=3:4;
PrivateNetwork=true
```

Let's stop nginx and lets start the socket and curl the port 80

```
[root@eth50-1 ~]# systemctl stop nginx.{socket,service}
[root@eth50-1 ~]# systemctl start nginx.socket
[root@eth50-1 ~]# curl -I localhost:80
```
```yaml
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Mon, 20 Feb 2023 19:10:04 GMT
Content-Type: text/html
Content-Length: 8474
Last-Modified: Mon, 28 Mar 2022 19:46:48 GMT
Connection: keep-alive
ETag: "624210a8-211a"
Accept-Ranges: bytes
```

## Change the Service User from root to nginx.

Ok this still works (by the way our exposure score went down to 7.0). Time to change the user! We need to make some changes...

First the systemd unit settings:

```ini
[~/] systemctl edit nginx.service
...
[Service]
# ...
User=nginx
Group=nginx
CapabilityBoundingSet=
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Manage /var/run/nginx
RuntimeDirectory=nginx
# Manage /var/lib/nginx
StateDirectory=nginx
# Manage /var/cache/nginx
CacheDirectory=nginx
# Manage /etc/nginx
ConfigurationDirectory=nginx

```

First to the nginx config, remove the user `user nginx;` and the `pid /run/nginx.pid;` configs:

```yaml
  1 # For more information on configuration, see:
  ...
  6 error_log syslog:server=unix:/dev/log;
  7 pid /var/run/nginx/nginx.pid;
  ...
```

And let's test nginx again, but first remove the old log directory (as it was originally created by root, not nginx):

```
[root@eth50-1 ~]# rm -rf /var/log/nginx/
[root@eth50-1 ~]# systemctl stop nginx.{socket,service}
[root@eth50-1 ~]# systemctl start nginx.socket
[root@eth50-1 ~]# curl -I localhost:80
```

The security just drop top 4.8... we made it... final things to add, that might be over kill:

# The Overkill

```ini
[service]
# ...
ProtectSystem=strict
LockPersonality=true
ProtectHostname=true
ProtectClock=true

SystemCallArchitectures=native
RestrictSUIDSGID=true
RemoveIPC=true
NoNewPrivileges=true

UMask=077

```

And exposure score drops to 4.0. All of these options can be found in the [systemd.exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html) man page.


* [`ProtectSystem=strict`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectSystem=): This option is used to protect the system's file system and other resources from modification by processes running as a non-root user. When set to "strict", it provides the strongest protection by disabling file system writes and limiting access to some system resources.

* [`LockPersonality=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#LockPersonality=): This option is used to prevent processes from changing the execution domain of the calling process, such as changing the personality of the program or the system architecture.

* [`ProtectHostname=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectHostname=): This option is used to prevent processes from modifying the hostname of the system.

* [`ProtectClock=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectClock=): This option is used to prevent processes from changing the system clock.

* [`SystemCallArchitectures=native`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#SystemCallArchitectures=): This option is used to restrict the system call interface to a specific architecture, limiting the attack surface by preventing execution of foreign code.

* [`RestrictSUIDSGID=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#RestrictSUIDSGID=): This option is used to prevent processes from executing with elevated privileges by restricting the use of setuid and setgid permissions.

* [`RemoveIPC=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#RemoveIPC=): All System V and POSIX IPC objects owned by the user and group the processes of this unit are run as are removed when the unit is stopped.

* [`NoNewPrivileges=true`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#NoNewPrivileges=): This option is used to prevent processes from acquiring new privileges after they have started running.

* [`UMask=077`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#UMask=): This option is used to set the default umask for all processes on the system, which controls the default file permissions for new files and directories created by processes.

## And ...

... we could go on, but you get the idea...

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)
