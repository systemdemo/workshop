WATCHDOG
--

watchdog is type of notify unit, in general we have seen that your unit can tell sytemd to shut them down, or inform 
about status changes. But what if the unit is frozen? and cant inform systemd that it needs restart?. Thats whats watchdog is for.

In a nutshell, if you set the option of watchdog in your service, then your service needs to send "watchdog pings" to systemd. if your service stop doing that, 
systemd will try to apply the stop policy, lets sea an example.

```commandline
systemctl start watchdog-demo1.service
```

You can see the unit is executed, it enter a start starte, and then its able to finish.

lets inspect the code



```commandline
systemctl cat watchdog-demo1.service
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd1.py
```

lets inspect another unit that will fail

```commandline
systemctl cat watchdog-demo2.service
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd2.py
```

In wd2.py we are sleeping for 10 seconds more than the allowed ping time, and the unit to fail... 

with 

```commandline
systemctl start watchdog-demo2.service
journalctl -f -u watchdog-demo2.service
```

we see the lines

```commandline
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Watchdog timeout (limit 3s)!
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Killing process 14488 (python3) with signal SIGABRT.
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Main process exited, code=dumped, status=6/ABRT
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Failed with result 'watchdog'.
```


we can try to catch that signal and exit gracefully, uncomment the signal catch in wd2.py

# changing watchdog parameters at runtime

you can change how frequent to expect pings from within the program, see wd3

```
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd3.py
systemctl start watchdog-demo3.service
journalctl -f -u watchdog-demo3.service
```

# asking systemd to issue a watchdog

```
systemctl start  watchdog-demo5.service
```

# unset watchdog

```
systemctl start  watchdog-unset.service
```

