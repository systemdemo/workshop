Notify Units
================

In this section, we will discuss a special type of unit: notify units. You can read more about different types of services [here](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#Type=).

> Behavior of notify is similar to exec; however, it is expected that the service sends a "READY=1" notification message via sd\_notify(3) or an equivalent call when it has finished starting up. systemd will proceed with starting follow-up units after this notification message has been sent.
> 
> 

The simplest way to explain this is that notify units can communicate their state to systemd and inform systemd.

Let's see how this affects startup.

Startup
------

If a unit is of type=notify, then in order for systemd to mark it as "having started" and continue with the next unit, the service itself needs to notify systemd that it has started. Let's see what exactly this means with a unit that won't notify.

Start by inspecting `basic-notify-not.service` with:
```bash
systemctl cat basic-notify-not.service
```
You might notice:
```makefile
...
[Service]
Type=notify
...
ExecStart=/usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py
...
```
Go ahead and execute `/usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py` and see its output.

Now start the unit:
```bash
systemctl start basic-notify-not.service
```
```bash
Job for basic-notify-not.service failed because a timeout was exceeded.
See "systemctl status basic-notify-not.service" and "journalctl -xeu basic-notify-not.service" for details.
```
It waited for 3 seconds and then failed... let's check the status:
```bash
systemctl status basic-notify-not.service
```
```markdown
× basic-notify-not.service - A notify service that decides not to notify
     Loaded: loaded (/etc/systemd/system/basic-notify-not.service; linked; preset: disabled)
     Active: failed (Result: timeout) since Tue 2024-03-12 22:55:43 UTC; 16s ago
    Process: 6131 ExecStart=/usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wont-notity.py (code=killed, signal=TERM)
   Main PID: 6131 (code=killed, signal=TERM)
        CPU: 13ms
Mar 12 22:55:40 localhost.localdomain systemd[1]: Starting basic-notify-not.service - A notify service that decides not to notify...
Mar 12 22:55:43 localhost.localdomain systemd[1]: basic-notify-not.service: start operation timed out. Terminating.
Mar 12 22:55:43 localhost.localdomain systemd[1]: basic-notify-not.service: Failed with result 'timeout'.
Mar 12 22:55:43 localhost.localdomain systemd[1]: Failed to start basic-notify-not.service - A notify service that decides not to notify.
```
You can see it's failing... now let's look at how we would notify.

Start the unit:
```bash
systemctl start basic-notify-yes.service
```
It starts immediately, and we can check the status with:
```bash
systemctl status basic-notify-yes.service
```
```markdown
○ basic-notify-yes.service - A notify service that decides not to notify
     Loaded: loaded (/etc/systemd/system/basic-notify-yes.service; linked; preset: disabled)
     Active: inactive (dead)
Mar 12 23:12:11 localhost.localdomain systemd[1]: Starting basic-notify-yes.service -
A notify service that decides not to notify...
Mar 12 23:12:11 localhost.localdomain systemd[1]: Started basic-notify-yes.service - A notify service that decides not to notify.
Mar 12 23:12:14 localhost.localdomain will-notity.py[6575]: I refuse to notify
Mar 12 23:12:14 localhost.localdomain will-notity.py[6575]: Will this line be reached?
Mar 12 23:12:14 localhost.localdomain systemd[1]: basic-notify-yes.service: Deactivated successfully.
```
Notice how we now have the output of the program! Why?

If we inspect [will-notify](will-notity.py), we see an important line:

```python
pystemd.daemon.notify(False, ready=1)
```
This just sends a message to systemd that we are ready to be loaded.

Let's play a bit with an interactive shell. Set your split tmux:

```bash
tmux
^B %
```
On one terminal, execute:
```bash
systemd-run --pty --service-type notify --unit tnot.service pystemd-shell
```
And in another, just type:

```bash
watch systemctl status tnot
```
Command to try to see what changes:
```python
pystemd.daemon.notify(False, ready=1)
pystemd.daemon.notify(False, status="this is my status, and I'm proud of it")
pystemd.daemon.notify(False, reloading=1)
pystemd.daemon.notify(False, ERRNO=42)
pystemd.daemon.notify(False, EXIT_STATUS="I'm a en exit status")
```
## Ones you can't undo are

* Removes notify socket
```python
pystemd.daemon.notify(True, ready=1)
```
* Signal shutting down
```python
pystemd.daemon.notify(False, stopping=1)
```
# Changing the main PID

In your `pystemd-shell`, start a new daemon process. You can see that:
```css
p = subprocess.Popen("nohup /bin/sleep 30", shell=True)
```
In your status, you can see that there are two processes in your group. In my case, it's:
```markdown
     CGroup: /system.slice/tnot.service
             ├─8583 python3 /usr/local/src/workshop/bin/pystemd-shell
             └─8601 /bin/sleep 30
```
If you exit now, then systemd would kill the remaining process (you can check). But you can instruct systemd to follow the other PID by doing:
```python
pystemd.daemon.notify(False, mainpid=p.pid)
```
Then the main PID has changed:
```markdown
   Main PID: 8668 (sleep)
```
If you exit now, systemd will do its best to monitor the main PID, and when it's gone, it will shut down the unit.

# Who can send notify signals, and helpers?

What's special about this notify signal, and can it be sent by any process?

Well... it depends. Let's see two examples:

Let's see a simple [bash script](notify-shell.sh) to illustrate this:
```bash
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/notify-shell.sh
```
It's straightforward... we "notify" systemd that we are ready using [systemd-notify](https://www.freedesktop.org/software/systemd/man/latest/systemd-notify.html) and then exec into sleep. Let's activate this by calling one service.

```bash
systemctl start root-notify-bash.service
systemctl status root-notify-bash.service
```
This "worked" and the service started, we regained control right away, and status tells
us that the status is `Status: "Waiting for data…"`

Let's try another unit:
```bash
systemctl start fail-notify-bash.service
systemctl status fail-notify-bash.service
```
You'll see the message:
```markdown
Mar 13 00:53:01 localhost.localdomain systemd[1]: fail-notify-bash.service: Got notification message from PID 11227, but reception only permitted for main PID 11226
Mar 13 00:53:04 localhost.localdomain systemd[1]: fail-notify-bash.service: start operation timed out. Terminating.
Mar 13 00:53:04 localhost.localdomain systemd[1]: fail-notify-bash.service: Failed with result 'timeout'.
```
But why?

```bash
systemctl cat fail-notify-bash.service
```
```makefile
# /etc/systemd/system/fail-notify-bash.service
[Unit]
Description=A notify service that tries to bash notify, but fails
[Service]
Type=notify
User=nobody
TimeoutStartSec=3s
ExecStart=/bin/bash /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/notify-shell.sh
```
The trick is `User=nobody`. By default, notify only accepts messages from the main PID, since bash has to execute `systemd-notify` that process is not "the main process". But why did it work for the first one?...
> systemd-notify will first attempt to invoke sd\_notify() pretending to have the PID of the parent process of systemd-notify (i.e. the invoking process). This will only succeed when invoked with sufficient privileges. On failure, it will then fall back to invoking it under its own PID.
> 
> 

How can we fix this... try:
```bash
systemctl start not-fail-notify-bash.service
systemctl status not-fail-notify-bash.service
```
```bash
systemctl cat not-fail-notify-bash.service
```
and notice `NotifyAccess=all`.