# Journal 101


## Log Config

Like most systemd daemons, systemd-journald has a set of properties are are specific to the daemon itself, as well as properties that can be found in unit configurations. The daemon specific properties are set in `/etc/systemd/journald.conf` and its corresponding override files. You can learn more about them in the man 5 page `journald.conf`.

Let's look at some commonly used properties, along with their defaults, that are specific to the systemd-journald daemon:

```ini
[Journal]
Storage=auto

RateLimitIntervalSec=30s
RateLimitBurst=10000

SystemMaxUse=
SystemKeepFree=
SystemMaxFileSize=
SystemMaxFiles=100
RuntimeMaxUse=
RuntimeKeepFree=
RuntimeMaxFileSize=
RuntimeMaxFiles=100

MaxRetentionSec=
MaxFileSec=1month

ForwardToSyslog=no
ForwardToKMsg=no
ForwardToConsole=no
ForwardToWall=yes

MaxLevelStore=debug
MaxLevelSyslog=debug
MaxLevelKMsg=notice
MaxLevelConsole=info
MaxLevelWall=emerg
```

The `Storage=` property controls where the logs are stored. It can be set to one of the following values:
- `volatile`: The logs will only be stored in memory and will not be saved to disk.
- `persistent`: The logs will be stored only on disk and not in memory.
- `auto`: Behaves like "persistent" if the `/var/log/journal` directory exists, and "volatile" otherwise (the existence of the directory controls the storage mode).
- `none`: Logs are not stored, but forwarding will still be functional.

The `RateLimitIntervalSec=` and `RateLimitBurst=` properties set the default log rate limit for a service. So by default a service cannot log more than `RateLimitBurst=` messages every `RateLimitIntervalSec=` seconds.

The `SystemMaxUse=`, `SystemKeepFree=`, `SystemMaxFileSize=`, `SystemMaxFiles=`, `RuntimeMaxUse=`, `RuntimeKeepFree=`, `RuntimeMaxFileSize=`, `RuntimeMaxFiles=` properties enforce limits on the journal files stored. The "System" properties apply to persistent (under `/var/log/journal`) journals and the "Runtime" properties apply to volatile (under `/run/log/journal`) journals.

By default, the "max use" properties default to 10%, and the "keep free" properties default to 15% of the size of the respective file system. Each value is capped to 4G. Archived/rotated journals are deleted if the limit is hit.
`SystemMaxFileSize=` and `RuntimeMaxFileSize=` control individual journal files and default to 1/8th of the values configured  for "max use". So normally there 7 rotated journals available.

`SystemMaxFiles=` and `RuntimeMaxFiles=` control the maximum number of journal files to retain. Archived/rotated journals are deleted if the limit is hit.

`MaxFileSec=` is a time-based (vs. size-based above) way to control the rotation of journals. `MaxRetentionSec=` is a time-based way to control when journals should get deleted.

`ForwardToSyslog=`, `ForwardToKMsg=`, `ForwardToConsole=`, and `ForwardToWall=` as the names suggest will forward logs from the journal to traditional syslog daemons, the kernel log buffer (kmsg), the system console, or as wall messages, respectively.

`MaxLevelStore=`, `MaxLevelSyslog=`, `MaxLevelKMsg=`, `MaxLevelConsole=`, and `MaxLevelWall=` control the max level of log messsages that are stored or forwarded. The rest are filtered out. Takes a syslog level as a string ("emerg", "alert", "crit", "err", "warning", "notice", "info", "debug") or integer (0-7).

At the service level you can also explore properties from man 5 page `systemd.exec`. Here's an example:

```ini
[Service]
StandardOutput=journal
StandardError=inherit

LogLevelMax=
LogExtraFields=

LogRateLimitIntervalSec=
LogRateLimitBurst=
```

`LogRateLimitIntervalSec=`, `LogRateLimitBurst=`, and `LogLevelMax=` override their respective systemd-journald daemon properties.

`StandardOutput=` and `StandardError=` control where stdout and stderr from the service go. It defaults to the journal but you can ignore the journal and also log straight to a file, socket, etc.

`LogExtraFields=` allows you to attach additional metadata fields to your logs. You'll learn more about metadata below.

## Basics of Viewing Journal Logs

As you saw earlier in the workshop, you can view journal logs by simply running:

```
[~] journalctl
```

Without any arguments this will show you all the logs starting from the oldest to newest. This can be slow so what I frequently do is sort from newest to oldest:

```
[~] journalctl -r
```

You can also filter the view by time range using `--since` and `--until`. You can pass dates, time stamps, or even relative values. For example to view logs from the last hour:

```
[~] journalctl --since -1hr
```

Earlier in the workshop we also used:

```
[~] journalctl -n 30 --no-hostname
```

This shows you the 30 newest log events and omits the hostname from view. Hostname can be redundant when you're looking at logs from the same system. However it can become useful when you share journal files and start looking at logs from a different system. TODO

## Let's write to the journal

We'll go over 3 different ways you can write to the journal. In the next section we'll look in the journal to see what we've written.

First, we'll do this via a service. We've provided a simple service called `journal_hello.service` that will echo a string and exit.

> Exercise: Examine the contents of `journal_hello` using `systemctl`.

Let's run the service:

```
[~] systemctl start journal_hello
```

Systemd ships with a utility called `systemd-cat` that also allows you to run a command and log output to the journal. Let's run it:

```
systemd-cat echo "Hello from systemd cat!"
```

Now to programmatically log to the journal. We've provided the source for a simple C file at `/opt/workshop/JOURNAL_101/journal_print.c`. These are the contents:

```C
#include <systemd/sd-journal.h>

int main(int argc, char *argv[]) {
        sd_journal_print(LOG_INFO, "Hello from programmatic journal print!");
        return 0;
```

Let's compile and run the program:

```
[~] gcc -l systemd /opt/workshop/JOURNAL_101/journal_print.c
[~] ./a.out
```

Now search for the logs we've generated by using `journalctl`'s `grep` functionality:

```
[~] journalctl -g Hello*
```

You should see all the log lines from the 3 different ways we talked to the journal. It also shows you which program sent the log line.

If you wanted to only see the logs that came from `journal_hello.service` you can filter by unit:

```
[~] journalctl -u journal_hello.service
```

Earlier I mentioned metadata. Each journal log in systemd has a bunch of metadata attached by default. Let's look at the metadata fields for `journal_hello.service`:

```
[~] journalctl -u journal_hello.service --output verbose
```

Fields that start with an underscore are added by the journal itself and cannot be modified by the client. Other fields can be set by the sending client. You'll see some pretty neat metadata as part of the output. Some of my favorites are `_CMDLINE`, `_SYSTEMD_CGROUP`, and `_PID`.

> Exercise: Remember the message we sent from `systemd-cat`? Figure out which unit it came from.

Armed with the knowledge of metadata fields, you can now do things like view logs from PID 1, or filter on unit messages that came from PID 1:

```
[~] journalctl _PID=1
[~] journalctl -u journal_hello.service _PID=1
```

## Journal is System-Wide

One of the things you may have noticed is that journal collects logs from the entire system. But not just unit logs, it also interleaves these with logs from the kernel. If you wanted to view only the kernel logs:

```
[~] journalctl --dmesg
```

All of the logs can be filtered by boot ID. So if you're interested in only logs from the current boot or the previous boot, you can do that.

To see the different log boot IDs and the time ranges associated:

```
[~] journalctl --list-boots
```

To only view the logs from the current boot:

```
[~] journalctl -b
```

> Exercise: What is the priority associated with the first kernel message of the current boot?

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)
