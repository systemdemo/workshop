WATCHDOG
==========

Watchdog is a type of notify unit. In general, we have seen that your unit can tell systemd to shut them down or inform about status changes. But what if the unit is frozen and can't inform systemd that it needs restart? That's what watchdog is for.

In a nutshell, if you set the option of watchdog in your service, then your service needs to send "watchdog pings" to systemd. If your service stops doing that, systemd will try to apply the stop policy. Let's see an example.
```commandline
systemctl start watchdog-demo1.service
```
You can see the unit is executed, it enters a start state, and then it's able to finish.

Let's inspect the code:
```commandline
systemctl cat watchdog-demo1.service
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd1.py
```
Now let's inspect another unit that will fail:
```commandline
systemctl cat watchdog-demo2.service
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd2.py
```
In wd2.py, we are sleeping for 10 seconds more than the allowed ping time, causing the unit to fail...
```commandline
systemctl start watchdog-demo2.service
journalctl -f -u watchdog-demo2.service
```
We see the following lines:
```commandline
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Watchdog timeout (limit 3s)!
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Killing process 14488 (python3) with signal SIGABRT.
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Main process exited, code=dumped, status=6/ABRT
Mar 13 02:17:55 localhost.localdomain systemd[1]: watchdog-demo2.service: Failed with result 'watchdog'.
```
We can try to catch that signal and exit gracefully by uncommenting the signal catch in wd2.py.

## Changing Watchdog Parameters at Runtime

You can change how frequently to expect pings from within the program, as shown in wd3:
```bash
cat /usr/local/src/workshop/workshop/SYSTEMD_FOR_DEVELOPERS/wd3.py
systemctl start watchdog-demo3.service
journalctl -f -u watchdog-demo3.service
```
## Asking Systemd to Issue a Watchdog

```bash
systemctl start  watchdog-demo5.service
```
## Unset Watchdog

```bash
systemctl start  watchdog-unset.service
```