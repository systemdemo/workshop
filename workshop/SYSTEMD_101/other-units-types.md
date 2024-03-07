# Other systemd unit types

systemd supports several types of units, each designed to manage different aspects of the system.

## Timers

Systemd timers are a powerful feature of the systemd init system that allow you to schedule the execution of specific tasks on your system. Similar to cron jobs, systemd timers enable you to run scripts, execute commands, or start services at specific times, or on specific intervals. However, unlike traditional cron jobs, systemd timers are more flexible, more accurate, and provide better logging and error reporting. But they can be a bit hard to understand.
In addition to their flexibility and accuracy, systemd timers offer several other advantages over traditional cron jobs, such as the ability to start tasks after a delay, handle failures more gracefully, and allow for more fine-grained control over when tasks are executed. Overall, systemd timers provide a more robust and reliable way to manage scheduled tasks on your system.

### Realtime timers

Traditionally when you setup a cron job, the information of when to execute, and what to execute are together in a single line, for instance

```
*/10 * * * * /usr/local/bin/check-disk-space
```

In systemd you create a [Timer unit](https://www.freedesktop.org/software/systemd/man/systemd.timer.html), that specifies “when to invoke a service unit”, and you specify the service unit that specifies “what to run”.

For instance let’s create `myfirsttimer`, that will execute  service-whoami.py every 30 seconds

```ini
[~] systemctl edit --force --full myfirsttimer.timer
…

[Unit]
Description=My first timer

[Timer]
OnCalendar=*-*-* *:*:00/30

[Install]
WantedBy=timers.target

```

```ini
[~] systemctl edit --force --full myfirsttimer.service
…

[Unit]
Description=My first systemd service

[Service]
Type=oneshot
ExecStart=/usr/bin/python /opt/bin/service-whoami.py
Environment=NO_SLEEP=no

[Install]
WantedBy=multi-user.target
```

Now execute

```bash
[~] systemctl start myfirsttimer.timer
[~] watch systemctl status myfirsttimer.{timer,service}
```

Status will show you data, using `watch` can show you the changes, specially  the `Trigger` field.

```yaml
● myfirsttimer.timer - My first timer
     Loaded: loaded (/etc/systemd/system/myfirsttimer.timer; disabled; preset: disabled)
     Active: active (waiting) since Tue 2023-02-21 17:23:00 UTC; 2s ago
      Until: Tue 2023-02-21 17:23:00 UTC; 2s ago
    Trigger: Tue 2023-02-21 17:23:30 UTC; 27s left
   Triggers: ● myfirsttimer.service

```

The output is:

* `Loaded`: This shows whether the unit file for the timer has been loaded by systemd. In this case, the timer has been loaded from the file /etc/systemd/system/myfirsttimer.timer.

* `Active`: This shows the current state of the timer. In this case, it is "active" and "waiting". This means that the timer is currently waiting for its trigger time to arrive.

* `Since`: This shows when the timer was last activated. In this case, it was activated 2 seconds ago at Tue 2023-02-21 17:23:00 UTC.

* `Until`: This shows when the timer is scheduled to stop waiting. In this case, the timer will stop waiting as soon as the current time reaches `Tue 2023-02-21 17:23:00 UTC`, which was 2 seconds ago.

* `Trigger`: This shows the exact time when the timer will trigger its associated service. In this case, the trigger time is set to `Tue 2023-02-21 17:23:30 UTC`, which is 27 seconds from the time the output was generated.

* `Triggers`: This shows the name of the systemd service that will be triggered by the timer when the trigger time is reached. In this case, the service name is `myfirsttimer.service`.

This is what we call realtime (i.e wallclock) timer, the [`OnCalendar`](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#OnCalendar=) define when systemd will activate the service unit based on the internal clock, clocks can move forward on back, can be reset and manipulated, this means that something can could run twice or skip a run.

### Monotonic timers
Timers also provide the [monotonic timers](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#OnActiveSec=); monotonic time is used to measure the amount of time that has passed since an arbitrary point in the past, and it is not affected by time adjustments or changes in the system clock.

You can do things like: trigger services to be executed 5 minutes after the system has booted,  or after a unit has been deactivated, etc. you do this by

```ini
[~] systemctl edit --full myfirsttimer.timer
…

[Unit]
Description=My first timer

[Timer]
OnActiveSec=30s

[Install]
WantedBy=timers.target
```

To start a unit 30 seconds after the service has started, and never again. All this settings can be combined and you can end up with something like:

```ini
[Unit]
Description=My first timer

[Timer]
OnCalendar=*-*-* *:*:00/30
OnActiveSec=5s
OnBootSec=100h

[Install]
WantedBy=timers.target
```

### Creating a ephemeral timer

If you just need a fire and forget type of thing… you can use systemd-run to create ad-hoc systemd timers.

Execute
```bash
[root@eth50-1 ~] systemd-run --on-active=30s echo "hello from the past"
Running timer as unit: run-r85fe61d719b34fe5a6938681d01c2ff8.timer
Will run service as unit: run-r85fe61d719b34fe5a6938681d01c2ff8.service
```
Then you can just `systemctl status run-r85fe61d719b34fe5a6938681d01c2ff8.{service,timer}`

Before it runs

```yaml
○ run-r85fe61d719b34fe5a6938681d01c2ff8.service - /usr/bin/echo hello from the past
     Loaded: loaded (/run/systemd/transient/run-r85fe61d719b34fe5a6938681d01c2ff8.service; transient)
  Transient: yes
     Active: inactive (dead)
TriggeredBy: ● run-r85fe61d719b34fe5a6938681d01c2ff8.timer

● run-r85fe61d719b34fe5a6938681d01c2ff8.timer - /usr/bin/echo hello from the past
     Loaded: loaded (/run/systemd/transient/run-r85fe61d719b34fe5a6938681d01c2ff8.timer; transient)
  Transient: yes
     Active: active (waiting) since Tue 2023-02-21 17:59:02 UTC; 21s ago
      Until: Tue 2023-02-21 17:59:02 UTC; 21s ago
    Trigger: Tue 2023-02-21 17:59:32 UTC; 8s left
   Triggers: ● run-r85fe61d719b34fe5a6938681d01c2ff8.service
```

While its running

```yaml

● run-r85fe61d719b34fe5a6938681d01c2ff8.service - /usr/bin/echo hello from the past
     Loaded: loaded (/run/systemd/transient/run-r85fe61d719b34fe5a6938681d01c2ff8.service; transient)
  Transient: yes
     Active: active (running) since Tue 2023-02-21 17:59:33 UTC; 7ms ago
TriggeredBy: ● run-r85fe61d719b34fe5a6938681d01c2ff8.timer
   Main PID: 10021 ((echo))
      Tasks: 1 (limit: 1112)
     Memory: 180.0K
        CPU: 335us
     CGroup: /system.slice/run-r85fe61d719b34fe5a6938681d01c2ff8.service
             └─10021 "(echo)"

Feb 21 17:59:33 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: Started run-r85fe61d719b34fe5a6938681d01c2ff8.service - /usr/bin/echo hello from the past.

● run-r85fe61d719b34fe5a6938681d01c2ff8.timer - /usr/bin/echo hello from the past
     Loaded: loaded (/run/systemd/transient/run-r85fe61d719b34fe5a6938681d01c2ff8.timer; transient)
  Transient: yes
     Active: active (running) since Tue 2023-02-21 17:59:02 UTC; 31s ago
      Until: Tue 2023-02-21 17:59:02 UTC; 31s ago
    Trigger: n/a
   Triggers: ● run-r85fe61d719b34fe5a6938681d01c2ff8.service

```

After it runs

```yaml
[~] systemctl status run-r85fe61d719b34fe5a6938681d01c2ff8.{service,timer}
Unit run-r85fe61d719b34fe5a6938681d01c2ff8.service could not be found.
Unit run-r85fe61d719b34fe5a6938681d01c2ff8.timer could not be found.

```

You can check [systemd-run](https://www.freedesktop.org/software/systemd/man/systemd-run.html#--on-active=) man page for other options.

### Randomize delay

A common error is to set all your timers at the same time (e.g. run some workload at beginning of that). Setting all timers to trigger at the same time can cause a sudden spike in system activity, which can lead to system overload and performance issues. This can be especially problematic in systems with a large number of timers.

To avoid this issue, systemd provides randomized options, [`RandomizedDelaySec`](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#RandomizedDelaySec=) and [`FixedRandomDelay`](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#FixedRandomDelay=) work to splay the execution of your timer in a window of time. try:


```ini
[Unit]
Description=My first timer

[Timer]
OnCalendar=*-*-* *:*:00/30
RandomizedDelaySec=10s

[Install]
WantedBy=timers.target
```

> Question: What does it do?.

### Extra options we wont cover:

Take a look at [`WakeSystem`](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#WakeSystem=) and [`OnClockChange=, OnTimezoneChange=`](https://www.freedesktop.org/software/systemd/man/systemd.timer.html#OnClockChange=) as they are edge cases, but useful never the less.


## Path

systemd can monitor a path, and “activate” a service unit when changes to that path path  happen. This can be useful to trigger a reload (or a restart) on a configuration for the service.


For instance lets automatically reload sshd whenever its configuration file changes

Create a file named ssh-config-watcher.path in either by creating directly in `/etc/systemd/system/` directory, or executing systemctl edit.

```bash
[~] systemctl edit --full --force ssh-config-watcher.path
```
```ini
[Unit]
Description=Watch for changes to sshd configuration

[Path]
PathChanged=/etc/ssh/sshd_config

[Install]
WantedBy=multi-user.target
```

This unit will watch for changes to the /etc/ssh/sshd_config file.

Create a file named ssh-config-watcher.service in the same directory or also by using systemctl edit.

Add the following contents to the nginx-config-watcher.service file:

```
[~] systemctl edit --full --force ssh-config-watcher.service
```
```ini
[Unit]
Description=reload sshd when configuration changes
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/systemctl reload sshd.service

[Install]
WantedBy=multi-user.target

```


Now start the ssh-config-watcher.path

```bash
[~] systemctl enable ssh-config-watcher.path
[~] systemctl start ssh-config-watcher.path
```
This will start the unit and ensure it starts automatically at boot time.

After completing the above steps, whenever the configuration file is modified, the sshd.service unit will be reloaded automatically.

Check status of sshd

```bash
[~] systemctl status sshd.service
```
```yaml
● sshd.service - OpenSSH server daemon
     Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled; preset: enabled)
     Active: active (running) since Tue 2023-02-21 21:31:56 UTC; 20s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 11892 ExecReload=/bin/kill -HUP $MAINPID (code=exited, status=0/SUCCESS)
   Main PID: 11882 (sshd)
      Tasks: 1 (limit: 1112)
     Memory: 1.4M
        CPU: 29ms
     CGroup: /system.slice/sshd.service
             └─11882 "sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups"

```

Now lets simulate a change in `/etc/ssh/sshd_config` by uncommenting like 34 and 35 to

```yaml
 33 # Logging
 34 SyslogFacility AUTH
 35 LogLevel INFO
 36
```

You could just touch the file to be honest

```bash
[~] systemctl status sshd.service
```
```yaml
● sshd.service - OpenSSH server daemon
     Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled; preset: enabled)
     Active: active (running) since Tue 2023-02-21 21:32:29 UTC; 18min ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 12147 ExecReload=/bin/kill -HUP $MAINPID (code=exited, status=0/SUCCESS)
   Main PID: 11903 (sshd)
      Tasks: 1 (limit: 1112)
     Memory: 1.3M
        CPU: 24ms
     CGroup: /system.slice/sshd.service
             └─11903 "sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups"
```

### Creating a ephemeral path

Same as an ephemeral timer, you can create ephemeral or ad-hoc path, we have cover this before, this is just an example

```
[~]# systemd-run --path-property PathExists=/tmp/ping touch /tmp/pong
Running path as unit: run-r1ad4c2faedb9498085f0090b6011ac50.path
Will run service as unit: run-r1ad4c2faedb9498085f0090b6011ac50.service
```
Will touch /tmp/pong when /tmp/ping is created, you can put any path property under [--path-property](https://www.freedesktop.org/software/systemd/man/systemd.path.html). Lets check that files dont exist


```
[~] ls /tmp/pong
ls: cannot access '/tmp/pong': No such file or directory
[~] ls /tmp/ping
ls: cannot access '/tmp/ping': No such file or directory
[~] ls /tmp/pong
ls: cannot access '/tmp/pong': No such file or directory
```

now lets create ping, and see pong been created.
```
[~] touch /tmp/ping
[~] ls /tmp/pong
/tmp/pong
```

---
[back to TOC](../README.md)
