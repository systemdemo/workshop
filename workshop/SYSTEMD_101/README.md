# Systemd 101


## Create your first unit

In this section we will get started with systemd. This will be our first try at working with systemd. If you have used systemd before, some of these things will look and feel familiar, but we need to walk before we can run, right?

To create your first systemd unit, you can save the contents to a file with a .service extension in the `/etc/systemd/system` directory. For example, you could create a file at `/etc/systemd/system/myfirstservice.service` with the contents:

```ini
[Unit]
Description=My first systemd service

[Service]
ExecStart=/usr/bin/python /opt/bin/service-whoami.py
Restart=always

[Install]
WantedBy=multi-user.target
```

This unit file assumes that you have a Python script located at `/opt/bin/service-whoami.py` (we already put it there for you). The `ExecStart` directive specifies the command to run when starting the service. The Restart directive specifies that the service should be automatically restarted if it crashes or exits for any reason. The `WantedBy` directive specifies that the service should be started as part of the multi-user.target, which is one of the default system states that systemd can bring the system into.


You can compare your unit to the one in /etc/systemd/system/myfirstservice-model.service to make sure you did not make a typo.

Once you've saved the unit file, you can use the following systemd commands to start your service:

```
[~] systemctl start myfirstservice.service
```

It would feel as if nothing happened. To view the status information for a systemd service unit, you can again use the `systemctl` command with the `status` option, Here's the syntax:

```
[~] systemctl status myfirstservice.service
```

The output will show you the current status of the service unit, including whether it's running or not, any errors or warnings that have occurred, and other details such as the process ID (PID) of the service.

Here's an example of what the output might look like:

```yaml
● myfirstservice.service - My first systemd service
     Loaded: loaded (/etc/systemd/system/myfirstservice.service; disabled; preset: disabled)
     Active: active (running) since Tue 2023-02-14 23:11:23 UTC; 2s ago
   Main PID: 7745 (sleep)
      Tasks: 1 (limit: 1112)
     Memory: 196.0K
        CPU: 48ms
     CGroup: /system.slice/myfirstservice.service
             └─7745 sleep infinity

Feb 14 23:11:23 systemd[1]: Started myfirstservice.service - My first systemd service.
```

In this example, the myfirstservice.service service unit is running and there are no errors or warnings reported. The service is being managed by systemd, and the process ID of the main Apache process is 7745. The output also shows the memory usage, approximately 198kb and the number of tasks (forks) associated with the service, it also shows that its barely using any CPU.

You can also see the cgroup attached to the service and the actual process tree thats been executing.

Finally you can stop your service with:

```
systemctl stop myfirstservice.service
```

And re check the status with status to see it stopped

```
[~] systemctl status myfirstservice.service
```
```yaml
○ myfirstservice.service - My first systemd service
     Loaded: loaded (/etc/systemd/system/myfirstservice.service; disabled; preset: disabled)
     Active: inactive (dead)
```

## Modify your first unit

> Note: make sure the unit is stop in for this section by executing `systemctl stop myfirstservice.service`

Now that we have started our first unit, we might want to modify it. There are 2 ways of doing this: modify the original service file, or add an override, let's start by modifying the original systemd unit. 


Let’s say that you want service to run as the user “vagrant”, we can use the property [User=vagrant](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#User=) option. 

Modify the original service file located in /etc/systemd/system/myfirstservice.service to looks like


```ini
[Unit]
Description=My first systemd service

[Service]
ExecStart=/usr/bin/python /opt/bin/service-whoami.py
Restart=always
User=vagrant

[Install]
WantedBy=multi-user.target
``` 

Note that if you try to start the unit, systemd will complain that it has changed since last execution (and also note that this has not happened the first time we run the unit)

```
[~] systemctl start myfirstservice.service

Warning: The unit file, source configuration file or drop-ins of myfirstservice.service changed on disk. Run 'systemctl daemon-reload' to reload units.
```

So run follow the instruction and run

```
[~] systemctl daemon-reload
```

And now you are free to start your service again and see the output of status.

```
[~] systemctl restart myfirstservice.service
[~] systemctl status myfirstservice.service
```

There is not much new in status that would indicate the unit is being run as an user other than root. Nevertheless, we have not seen the actual output of the command we are executing… we kind of trust that the command is there.

First, before seen whats the output of the service lest execute the command in the terminal

```
[~] /opt/bin/service-whoami.py
```

You see 3 sections, 1) the most beautiful ascii art banner ever created by humans, 2) a quick section that show data about the configuration of the running process, including the service name, the user that running the service and the pid and 3) the environmental variables availables… then the script just execv to sleep infinity waiting for your ctl-C to finish the process.

iIf you want to see output of a service unit, you need to execute 

```bash
[~] journalctl -n 30 --no-hostname -u myfirstservice.service 
```

And you will see the output.

```
[~] journalctl -n 30 --no-hostname -u myfirstservice.service 
Feb 15 00:07:54 python[8415]:  *                          _                     _                           _
Feb 15 00:07:54 python[8415]:  *                         (_)                   | |                         (_)
Feb 15 00:07:54 python[8415]:  *      ___  ___ _ ____   ___  ___ ___  __      _| |__   ___   __ _ _ __ ___  _
Feb 15 00:07:54 python[8415]:  *     / __|/ _ \ '__\ \ / / |/ __/ _ \ \ \ /\ / / '_ \ / _ \ / _` | '_ ` _ \| |
Feb 15 00:07:54 python[8415]:  *     \__ \  __/ |   \ V /| | (_|  __/  \ V  V /| | | | (_) | (_| | | | | | | |
Feb 15 00:07:54 python[8415]:  *     |___/\___|_|    \_/ |_|\___\___|   \_/\_/ |_| |_|\___/ \__,_|_| |_| |_|_|
…
myfirstservice.service
Feb 15 00:07:54 python[8415]:  User: vagrant
Feb 15 00:07:54 python[8415]:  Extra: uid=1000 gid=1000
Feb 15 00:07:54 python[8415]:  PID: 8415
Feb 15 00:07:54 python[8415]:  MAINPID: 8415
Feb 15 00:07:54 python[8415]: Environmental variables:
Feb 15 00:07:54 python[8415]:  {'HOME': '/home/vagrant',
Feb 15 00:07:54 python[8415]:   'INVOCATION_ID': '73d04e9d6d6f466396e2896b128ac562',
…
Feb 15 00:07:54 python[8415]: sleeping forever....
```


We will see more of journalctl later, but in the meantime we’ll explain that when you run the `journalctl -n 30 --no-hostname -u myfirstservice.service` command, it will display the 30 most recent log entries related to the myfirstservice service. 

## Creating overrides for units.

Another way of modifying systemd is to use an override file. An override file is a small configuration file that contains directives that will be applied on top of the directives in the original unit file.
When you create an override file for a unit, systemd reads the override file and applies the directives in it to the unit's configuration. This can be useful if you need to customize the behavior of a system service or if you want to apply temporary changes to a unit that you don't want to modify permanently.
An override file is a plain text file that follows a specific naming convention. The name of the file should be the name of the unit followed by the ".d" suffix, and it should be placed in the /etc/systemd/system/ directory (or in the /run/systemd/system/ directory for runtime overrides). For example, to create an override for the myfirstservice.service unit, to let’s say, add a new environmental variable to the process,  you would create a file named `/etc/systemd/system/myfirstservice.service.d/override.conf` containing only that setting.

You don’t really need to create this file by hand, you can use the systemctl edit command to create and edit the file. This command will open a new file in your default text editor and create the necessary directories if they don't already exist. Once you've added your directives to the override file, you can save and close the file, and then reload systemd to apply the changes. 

Execute

```
[~] systemctl edit myfirstservice.service
```

And add

```
[Service]
Environment=SPECIAL_ENV=activated
```

Save the file, execute the dance of 

```
[~] systemctl daemon-reload
[~] systemctl restart myfirstservice.service
[~] journalctl -n 15 -u myfirstservice.service -g "SPECIAL_ENV"

Feb 15 00:52:12 python[8530]:   'SPECIAL_ENV': 'activated',
```

Not all changes require a restart of the unit, it really depends on the implementation of the setting, so for instance namespace properties and “startup dependant conditions” like environment variables, depends on restarting the service unit, but cgroup properties can be applied to a life service like, Memory, CPU, Tasks, etc.

Edit the override file by either modifying `/etc/systemd/system/myfirstservice.service.d/override.conf` or executing `systemctl edit myfirstservice.service` to looks like:

```ini
[Service]
Environment=SPECIAL_ENV=activated
MemoryMax=10M
```

Note: that if you overwrite the override file directly (by using vim for instance), then you need to execute `systemctl daemon-reload` on your own, `systemctl edit` takes care of that for you.

Now execute 

```
[~] systemctl status myfirstservice.service
```

```yaml
● myfirstservice.service - My first systemd service                                                                                                           
     Loaded: loaded (/etc/systemd/system/myfirstservice.service; disabled; preset: disabled)
    Drop-In: /etc/systemd/system/myfirstservice.service.d
             └─override.conf
     Active: active (running) since Wed 2023-02-15 00:52:12 UTC; 13min ago
   Main PID: 8530 (sleep)
      Tasks: 1 (limit: 1112)
     Memory: 2.3M (max: 10.0M available: 7.6M)
        CPU: 47ms
     CGroup: /system.slice/myfirstservice.service
             └─8530 sleep infinity
``` 

And check `Memory: 2.3M (max: 10.0M available: 7.6M)` now has an upper limit without needing to restart the unit.


## Quick and dirty walthrough of some systemctl commands

Now we will quickly check a couple systemd commands that can get you started.

---
### systemctl status

We have used this before, it display a simple, yet very comprehensive status for a systemd unit, using it its simple just

```
systemctl status <unit-name>
``` 

When `unit-name` its a service unit (ends with .service), you don’t need to append .service, so both `systemctl status myfirstservice.service` and `systemctl status myfirstservice` are functionally equivalent.

Beside units `systemctl status` can accept a **PID** number (this does not need to be the main pid), for instance:

```
[~] systemctl status 9178
```

Will show the status of the service that’s running the process 9178.

> Exercise: find a pid in your system, and see what service is running it.

> Exercise: If every process (with a PID) on your machine is running under a systemd unit, whats the unit for PID 1? 

---

### systemctl cat

In order to display the content of a systemd unit (including all overrides ) systemctl cat can do this for you, in a simple way

```
[~] systemctl cat  myfirstservice.service   
```
```ini               
# /etc/systemd/system/myfirstservice.service
[Unit]                           
Description=My first systemd service
                                                                               
[Service]                           
ExecStart=/usr/bin/python /opt/bin/service-whoami.py
Restart=always
User=vagrant

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/myfirstservice.service.d/override.conf
[Service]
Environment=SPECIAL_ENV=activated
MemoryMax=10M
```

---
### systemctl show

While `systemctl status` shows a subset of properties of an unit, and `systemctl cat` shows the unit file, `systemctl show` allows you to view any/all properties of a systemd unit, such as a service or target.

By default, `systemctl show` displays all the properties of a unit. You can use the `-p` option to show a specific property, and you can use the `--value` option to display only the value of the property.


```
[~] systemctl show myfirstservice   
```

```ini
Type=simple                                                                                                                                                   
ExitType=main
Restart=always
NotifyAccess=none
RestartUSec=100ms
TimeoutStartUSec=1min 30s
TimeoutStopUSec=1min 30s
TimeoutAbortUSec=1min 30s
TimeoutStartFailureMode=terminate
TimeoutStopFailureMode=terminate
RuntimeMaxUSec=infinity
RuntimeRandomizedExtraUSec=0
WatchdogUSec=0
WatchdogTimestampMonotonic=0
RootDirectoryStartOnly=no
RemainAfterExit=no
GuessMainPID=yes
MainPID=9178
ControlPID=0
FileDescriptorStoreMax=0
…
```

Displays all the properties of a unit. And to only display a subset

```
[~] systemctl show -p MainPID -p ExecStart myfirstservice  
```

```ini
MainPID=9178
ExecStart={ path=/usr/bin/python ;  …
```


```
[~] systemctl show -p MainPID --value myfirstservice  

9178
```


---
### systemctl kill 

The `systemctl kill` command is used to send a signal to a running service. Without any arguments, same as kill, the signal that is sent by default is the SIGTERM signal, which is a signal that requests the service to gracefully shut down and release any resources it has been using.

Even though the signal sent is SIGTERM by default, you can send any signal, from SIGKILL to SIGWINCH. 

Try to:

```
systemctl kill --signal 9 myfirstservice 
```
And then check the status of the unit

```
systemctl status  myfirstservice.service    
```

You will see that we still have the unit running, but the startup time now its very recently. Since our unit its configured with `Restart=always`, then when the main process was killed by `systemctl kill --signal 9 myfirstservice ` systemd restart the unit immediately.

Check 

```
[~] journalctl –no-pager -u myfirstservice.service -g "myfirstservice.service: " 
```
And you’ll see

```
Feb 15 05:35:29 systemd[1]: myfirstservice.service: Sent signal SIGKILL to main process 9137 (sleep) on client request.
Feb 15 05:35:29 systemd[1]: myfirstservice.service: Main process exited, code=killed, status=9/KILL
Feb 15 05:35:29 systemd[1]: myfirstservice.service: Failed with result 'signal'.
Feb 15 05:35:29 systemd[1]: myfirstservice.service: Scheduled restart job, restart counter is at 1.
```

The difference between _kill_ and _stop_, is that when executing `systemctl stop myfirstservice.service` systemd will not honor the `Restart=` option on the unit, so it will remain stop.


# Using systemd-run to run transient (ad-hoc) services


Another incredible useful ability, is the ability to create units “on the fly”, to that intents
`systemd` ships with `systemd-run`, this allows users to create and manage transient system services and tasks.

To get started with it execute

```
[~]# systemd-run python /opt/bin/service-whoami.py 
Running as unit: run-r062113ac9377474ca5eaff8c7f5ca6c0.service
```

And that’s it, systemd will take for you (under the hood) to create an ephemeral unit that does just that… execute  python /opt/bin/service-whoami.py, it returns you the name of the unit `run-r062113ac9377474ca5eaff8c7f5ca6c0.service`. Go ahead and query the status of the unit

```yaml
[root@eth50-1 ~]# systemctl status run-r062113ac9377474ca5eaff8c7f5ca6c0.service
● run-r062113ac9377474ca5eaff8c7f5ca6c0.service - /usr/bin/python /opt/bin/service-whoami.py
     Loaded: loaded (/run/systemd/transient/run-r062113ac9377474ca5eaff8c7f5ca6c0.service; transient)
  Transient: yes
     Active: active (running) since Wed 2023-02-15 16:54:50 UTC; 1min 53s ago
   Main PID: 9457 (sleep)
      Tasks: 1 (limit: 1112)
     Memory: 192.0K
        CPU: 50ms
     CGroup: /system.slice/run-r062113ac9377474ca5eaff8c7f5ca6c0.service
             └─9457 sleep infinity

Feb 15 16:54:50 eth50-1.rsw1ah.30.frc4.tfbnw.net python[9457]:  MAINPID: 9457
Feb 15 16:54:50 eth50-1.rsw1ah.30.frc4.tfbnw.net python[9457]: Environmental variables:
Feb 15 16:54:50 eth50-1.rsw1ah.30.frc4.tfbnw.net python[9457]:  {'INVOCATION_ID': 'baeb86d1003b4444829604a7908d5021',

```

You can see that the output of status “looks and feel” like a real unit, the only thing that tells you that the unit is transient, it is that its located under `/run/systemd/transient/`

Lets inspect the content of the unit file created

```
[root@eth50-1 ~] systemctl cat run-r062113ac9377474ca5eaff8c7f5ca6c0.service
```

```ini
# /run/systemd/transient/run-r062113ac9377474ca5eaff8c7f5ca6c0.service
# This is a transient unit file, created programmatically via the systemd API. Do not edit.
[Unit]
Description=/usr/bin/python /opt/bin/service-whoami.py

[Service]
ExecStart=
ExecStart="/usr/bin/python" "/opt/bin/service-whoami.py"

```

Nothing much going on here, the only magic systemd did was convert your “python” into “/usr/bin/python”.

## Run an interactive shell

To run an interactive shell using systemd-run, you can use the --shell option to allocate a pseudo-terminal for the shell process. Here's an example:

```
[~] systemd-run --shell
Running as unit: run-u506.service
Press ^] three times within 1s to disconnect TTY.
[root@eth50-1 root]# 
```

Even tho they look like you are still in the same shell, you are not, you status your own pid by doing.

```
[~/ root]# systemctl status $$
● run-u507.service - /bin/bash
     Loaded: loaded (/run/systemd/transient/run-u507.service; transient)
  Transient: yes
     Active: active (running) since Wed 2023-02-15 17:35:16 UTC; 13min ago
   Main PID: 9770 (bash)
      Tasks: 3 (limit: 1112)
     Memory: 1.8M
        CPU: 30ms
     CGroup: /system.slice/run-u507.service
             ├─9770 /bin/bash
             ├─9896 systemctl status 9770
             └─9897 less
```

Now you see and execute commands “like you are inside the service", a pseudo container if you like. go ahead play around a bit, and then exit the shell

```
[~] exit
```

## Run an interactive process

Another interesting invocation, its to use -p to set properties, and --pty to connect stdin stdout and stderr back to your shell

```
[root@eth50-1 workshop]# systemd-run -p DynamicUser=true --pty python /opt/bin/service-whoami.py
Running as unit: run-u517.service
Press ^] three times within 1s to disconnect TTY.

/***
 *                          _                     _                           _ 
 *                         (_)                   | |                         (_)
 *      ___  ___ _ ____   ___  ___ ___  __      _| |__   ___   __ _ _ __ ___  _ 
 *     / __|/ _ \ '__\ \ / / |/ __/ _ \ \ \ /\ / / '_ \ / _ \ / _` | '_ ` _ \| |
 *     \__ \  __/ |   \ V /| | (_|  __/  \ V  V /| | | | (_) | (_| | | | | | | |
 *     |___/\___|_|    \_/ |_|\___\___|   \_/\_/ |_| |_|\___/ \__,_|_| |_| |_|_|
 *                                                                              
 *                                                                              
 */

#######################################
starting service whoami
runing as
 Service Unit: run-u517.service
 User: run-u517
 Extra: uid=61314 gid=61314
 PID: 10808
 MAINPID: 10808

Environmental variables:
 {'INVOCATION_ID': '619b71f0c1c146e4bbc0cb99fbb3db6c',
  'LANG': 'en_US.UTF-8',
  'LOGNAME': 'run-u517',
  'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin',
  'SYSTEMD101_DIR': '/opt/workshop/02 - systemd 101',
  'SYSTEMD_EXEC_PID': '10808',
  'TERM': 'screen-256color',
  'USER': 'run-u517',
  'WORKSHOP_DIR': '/opt/workshop'}

sleeping forever....

```

And as you can see the terminal is stuck waiting for you to send the ctl-C signal… go ahead and do that.

> Note: `systemd-run --pty bash` and  `systemd-run --shell` are functionally equivalent

> Note: you can run `systemd-run --pty ipython` to start an interactive ipython shell.

