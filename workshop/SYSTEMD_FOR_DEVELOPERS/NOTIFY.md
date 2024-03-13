notify units
--

In this section we will discuss a special types of units, they are the notify units.
you can read more about diferent types of services [here](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#Type=)
but from the docs:

> Behavior of notify is similar to exec; however, it is expected that the service sends a "READY=1" notification message via sd_notify(3) or an equivalent call when it has finished starting up. systemd will proceed with starting follow-up units after this notification message has been sent.

The simples way i have to explain this, is that notify unites can comunicate their state to systemd, and inform systemd.

lets see how this affect startp

Startup
--

If a unit it is of type=notify then in order for systemd to mark them  as 
"having started" and continue with the next unit, the service itself needs to notify it has started.
lets see what exactly does this means with a unit that wont notify

start by inspecting basic-notify-not.service with

```commandline
systemctl cat basic-notify-not.service
```

you might notice

```commandline
...

[Service]
Type=notify
...
ExecStart=/usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py
```

go ahead and execute /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py and see its output


now start the unit 

```commandline
systemctl start basic-notify-not.service 
```
```
Job for basic-notify-not.service failed because a timeout was exceeded.
See "systemctl status basic-notify-not.service" and "journalctl -xeu basic-notify-not.service" for details.
```

it waited for 3 seconds and then failed... let's check the status


```
systemctl status  basic-notify-not.service 
```
```
× basic-notify-not.service - A notify service that decide not to notify
     Loaded: loaded (/etc/systemd/system/basic-notify-not.service; linked; preset: disabled)
     Active: failed (Result: timeout) since Tue 2024-03-12 22:55:43 UTC; 16s ago
    Process: 6131 ExecStart=/usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py (code=killed, signal=TERM)
   Main PID: 6131 (code=killed, signal=TERM)
        CPU: 13ms

Mar 12 22:55:40 localhost.localdomain systemd[1]: Starting basic-notify-not.service - A notify service that decide not to notify...
Mar 12 22:55:43 localhost.localdomain systemd[1]: basic-notify-not.service: start operation timed out. Terminating.
Mar 12 22:55:43 localhost.localdomain systemd[1]: basic-notify-not.service: Failed with result 'timeout'.
Mar 12 22:55:43 localhost.localdomain systemd[1]: Failed to start basic-notify-not.service - A notify service that decide not to notify.
```

you can see its failing... now lets look at how would we notify.

```commandline
systemctl start basic-notify-yes.service 
```

it starts immediately and we can check the status with


```
systemctl status  basic-notify-yes.service 
```

```commandline
[root@localhost workshop]# systemctl status basic-notify-yes.service 
○ basic-notify-yes.service - A notify service that decide not to notify
     Loaded: loaded (/etc/systemd/system/basic-notify-yes.service; linked; preset: disabled)
     Active: inactive (dead)

Mar 12 23:12:11 localhost.localdomain systemd[1]: Starting basic-notify-yes.service - A notify service that decide not to notify...
Mar 12 23:12:11 localhost.localdomain systemd[1]: Started basic-notify-yes.service - A notify service that decide not to notify.
Mar 12 23:12:14 localhost.localdomain will-notity.py[6575]: I refuse to notify
Mar 12 23:12:14 localhost.localdomain will-notity.py[6575]: Will this line be reach?
Mar 12 23:12:14 localhost.localdomain systemd[1]: basic-notify-yes.service: Deactivated successfully.
```

notice how we now have the output of the program!. why?

if we inspect [will-notify](will-notity.py) we see an important line:

```commandline
pystemd.daemon.notify(False, ready=1)
```

This just send a message to systemd that we are ready to be loaded.

Lets play a bit with an interactive shell. set your split tmux

```commandline
tmux
^B %
```

on one terminal execute

```commandline
systemd-run --pty --service-type notify --unit tnot.service  pystemd-shell
```

and in another just type

```commandline
watch systemctl status tnot
```

command to try to see what changes:

```commandline
pystemd.daemon.notify(False, ready=1)
pystemd.daemon.notify(False, status="this is my status, and i'm proud of it")
pystemd.daemon.notify(False, reloading=1)
pystemd.daemon.notify(False, ERRNO=42)
pystemd.daemon.notify(False, EXIT_STATUS="i'm a en exit status")
```

## ones you cant undo are

* removes notify socket
```
pystemd.daemon.notify(True, ready=1)
```

* signal shutting down

```
pystemd.daemon.notify(False, stopping=1)
```


# changing the main pid

on your pystemd-shell, start a new deamon process, you can see that

```commandline
p = subprocess.Popen("nohup /bin/sleep 30", shell=True)
```

in your status you can see that there are 2 process on your group, in my case its

```commandline
     CGroup: /system.slice/tnot.service
             ├─8583 python3 /usr/local/src/workshop/bin/pystemd-shell
             └─8601 /bin/sleep 30
```

if you exit now, then systemd would kill the remaining process, (you can check), 
but you can instruct systemd to follow the other pid, by doing

```commandline
pystemd.daemon.notify(False, mainpid=p.pid)
```

then the main pid has changed

```commandline
   Main PID: 8668 (sleep)  
```


if you exit now, systemd will do it best to monitor the main pid, and when its gone will shutdown the unit

# who can send notify signals, and helpers?

What's special about this notify signal, and can be send by any process?

Well... it depends, lets see 2 examples:

lets see a simple [bash script](notify-shell.sh) to illustrate this

```commandline
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/notify-shell.sh
```

it's straightforward... we "notify" systemd that we are ready using [systemd-notify](https://www.freedesktop.org/software/systemd/man/latest/systemd-notify.html)
and then we exec into sleep. Lets activate this by calling one service.

```commandline
systemctl start root-notify-bash.service 
systemctl status root-notify-bash.service 
```

This "worked" and the service started, we regain control right away, and status tell us that the status is `Status: "Waiting for data…"`

Let's try another unit

```commandline
systemctl start fail-notify-bash.service 
systemctl status fail-notify-bash.service 
```

you'll see the messsage

```commandline
Mar 13 00:53:01 localhost.localdomain systemd[1]: fail-notify-bash.service: Got notification message from PID 11227, but reception only permitted for main PID 11226
Mar 13 00:53:04 localhost.localdomain systemd[1]: fail-notify-bash.service: start operation timed out. Terminating.
Mar 13 00:53:04 localhost.localdomain systemd[1]: fail-notify-bash.service: Failed with result 'timeout'.
```

but why?

```commandline
systemctl cat fail-notify-bash.service
```
```
# /etc/systemd/system/fail-notify-bash.service
[Unit]
Description=A notify service that tries to bash notify, but fails

[Service]
Type=notify
User=nobody
TimeoutStartSec=3s
ExecStart=/bin/bash /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/notify-shell.sh
```

The trick is `User=nobody`. By default notify only accept messages from the main pid, since bash has to execute 
systemd-notify that process is not "the main process". by why did it work for the first one?... 

> systemd-notify will first attempt to invoke sd_notify() pretending to have the PID of the parent process of systemd-notify (i.e. the invoking process). This will only succeed when invoked with sufficient privileges. On failure, it will then fall back to invoking it under its own PID. 

how can we fix this... try

```commandline
systemctl start not-fail-notify-bash.service 
systemctl status not-fail-notify-bash.service 
```


```commandline
systemctl cat not-fail-notify-bash.service
```

and notice `NotifyAccess=all`.


# extend startup time

So far our unit is expected to start in 3 seconds, that seems like a good default, 
but you can also change that during startup... 

```
systemctl start watchdog-demo4.service
```