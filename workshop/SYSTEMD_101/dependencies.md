# Dependencies and More

## Why Do Ordering and Dependencies Matter?

In the days of SysVinit, services were started sequentially at boot based on numbering. Systemd changes this by introducing the concept of dependencies and ordering. Instead of manually numbering your services based on where you think they should run, you can instead list all your dependencies in your unit file. Then systemd can use that information to parallelize start up and shutdown as much as possible. No more manual numbering!

## Ordering

You can order units in 2 ways: with `Before=` or `After=`. Let's say we have a dinosaur.service with `Before=human.service`. This tells systemd that when we are starting dinosaur.service and human.service at the same time, we order dinosaur.service before human.service. We can also do this the other way with `After=` if we have a human.service with `After=dinosaur.service`.

Let's try it out. We provided dinosaur.service and human.service. These are the contents:

```
[~] systemctl cat dinosaur.service
# /etc/systemd/system/dinosaur.service
[Unit]
Before=human.service

[Service]
ExecStart=echo rawr
RemainAfterExit=yes

[~] systemctl cat human.service
# /etc/systemd/system/human.service
[Service]
ExecStart=echo oogabooga
RemainAfterExit=yes
```

We want dinosaur.service to come before human.service. We use `RemainAfterExit=yes` to keep the state around so we can examine it even after the unit finishes. Let's start the units and examine the start times:

```
[~] systemctl start dinosaur.service human.service
[~] systemctl show -p ActiveEnterTimestampMonotonic dinosaur.service
[~] systemctl show -p ActiveEnterTimestampMonotonic human.service
```

You should see that the active enter timestamp for dinosaur.service comes before human.service.

## Dependencies

The basic unit dependency properties in systemd are `Requires=` and `Wants=`.

Let's say we have a life.service with `Requires=water.service`. This tells systemd that when we are starting life.service, we will also start water.service. If water.service fails to start, life.service will also fail to start. If `Before=` or `After=` are not provided, the units will start at roughly the same time.

We provided life.service and water.service for you to try it out. These are the contents:

```
[~] systemctl cat life.service
# /etc/systemd/system/life.service
[Unit]
Requires=water.service
After=water.service

[Service]
ExecStart=echo wow

[~] systemctl cat water.service
# /etc/systemd/system/water.service
[Service]
ExecStart=/bin/false
```

Let's see what happens when you try to start life.service:

```
[~] systemctl start life.service
[~] systemctl status life.service
[~] systemctl status water.service
```

life.service... ran? Successfully??? Why!? We should see that water.service failed, but life.service ran successfully. We expected to life.service to fail!


The devil is in the details: the wording is very clear that `Requires=` only refers to *starting* the unit. If you look closely at the logs for water.service, you will see that it did indeed *start* successfully, but the main process returned non-zero (failed). We can rework water.service to make it "fail to start" like so:

```
[~] systemctl edit water.service

# Add the following lines, save and exit
[Service]
Type=notify
```

What this does is tell systemd to only consider the unit started when your unit sends the `READY=1` message via `sd_notify`. With `Type=simple`, systemd only waits for the unit for fork before considering the unit "started". If you try it again, we should get a dependency error:

```
[~] systemctl start life.service
[~] systemctl status life.service
[~] systemctl status water.service
```

> Exercise: Keeping Type=notify on water.service, modify the ExecStart= for water.service to send a READY=1 message. Hint: use systemd-notify.


`Wants=` is a weaker dependency. With `Wants=` it does not matter if the wanted dependency starts successfully or not. Most of the time, `Wants=` dependency is what you *want* to use!

Let's see this in action. We provided 2 units: dog.service and bone.service. dog.service wants bone.service. Here are the contents:

```
[ ~] systemctl cat dog.service
# /etc/systemd/system/dog.service
[Unit]
Wants=bone.service

[Service]
Type=oneshot
ExecStart=echo woof

[~] systemctl cat bone.service
# /etc/systemd/system/bone.service
[Service]
Type=notify
ExecStart=/bin/false
```

So dog.service *wants* bone.service. However, bone.service is using `Type=notify` and `ExecStart=/bin/false` as in the previous example to force bone.service to fail to start. There are no ordering dependencies so they will start roughly together. We will demonstrate that this does not block dog.service from running successfully:

```
[~] systemctl start dog.service
[~] systemctl status dog.service
[~] systemctl status bone.service
```

Notice how starting dog.service also started bone.service. Also notice how dog.service successfully ran and echoed "woof", while bone.service failed.


## Install

In the previous examples where we use `Before=` and `After=` without dependencies, we started the units together in the same `systemctl` command. However, there are other situations where the units may be started at the same time, even without `Wants=` or `Requires=` dependencies. For example, if a unit is slated to start at boot, it will start at the same time as other units that will start at boot! And so we may need to explicitly order them.

The way to typically start services at the last stage of boot (for userspace set up) is by adding the following:

```
[Install]
WantedBy=multi-user.target
```

There are many other targets that you can use (and you can also make your own) to configure different stages of boot.

It is very important that you run *systemctl enable* on the unit to create the dependency symlink that starts the service at boot. Otherwise it just won't.

Let's do a quick experiment. First, copy the contents of dinosaur.service and human.service to new unit files under /etc/systemd/system (we need to do this because our current unit files are symlinks to /usr/local which doesn't necessarily work at boot):

```
[~] cp /etc/systemd/system/dinosaur.service /etc/systemd/system/a.service
[~] cp /etc/systemd/system/human.service /etc/systemd/system/b.service
```

Reboot:

```
[~] systemctl reboot
```

Now SSH back in and notice that a.service and b.service have not started:

```
[~] systemctl status a.service b.service
```

Add the `[Install]` contents from above to the 2 units and enable the units:

```
[~] systemctl edit a.service
[~] systemctl edit b.service
[~] systemctl enable a.service b.service
```

You will see that 2 symlinks were created. Now reboot, SSH back in, and notice the units ran!

## Synchronization

Based on the dependency chart for units, systemd can parallelize the bootup process as much as possible. And on shutdown, it also uses the same information to stop units in the reverse order they started. The man page for bootup has a great chart on how to visualize this:

```
[~] man bootup
```

You'll notice that the bootup chart consists of multiple target units. Services are further associated with a target like in the examples above. you can read about each of these targets in detail in the systemd.special man page.

Target units are used to set synchronization points for ordering dependencies with other unit files. You can think of targets as similar to runlevels in traditional SysVinit systems, but with more flexibility and granularity. Unlike other unit types, there is no special `[Target]` section for configuring a target unit, only the `[Unit]` section.

The default boot target is decided by what `/etc/systemd/system/default.target` is symlinked to. Check what target it is with:
```
[~] systemctl get-default
```
This is the same as checking the symlink for default.target.

## Creating a custom boot target
We've included a simple unit called pasta.target and its contents:
```
[~] systemctl cat pasta.target
# /etc/systemd/system/pasta.target
[Unit]
Description=My Very Pasta Target
Requires=multi-user.target
Conflicts=rescue.service rescue.target
After=multi-user.target rescue.service rescue.target
AllowIsolate=yes
```
multi-user.target is a special target unit for setting up a non-graphical multi-user system. Since pasta.target requires and runs after multi-user.target we can use it as a boot target. Let's set pasta.target as our default boot target:
```
[~] systemctl set-default pasta.target
```

What this command does it redirect default.target's symlink to point at the target you set. You can do this symlink redirection manually yourself, however there are safety checks in place in the command to prevent you from setting the boot target to something invalid. For example, if you get a `Failed to set default target: Refusing to operate on alias name or linked unit file: pasta.target` error, then it may be because pasta.target is a symlink rather than a file. (If this happens to you, remove the symlink and copy over the actual file in its place. Then try again.)

Remember that you can associate a service to this target in order to start the unit at that boot point. We've provided a simple one for you:
```
[~] systemctl cat noodle.service
# /etc/systemd/system/noodle.service
[Service]
ExecStart=/bin/echo "very noodley end"

[Install]
WantedBy=pasta.target
```

Now enable it (remember that unless you do this, the service will not start with the target):
```
[~] systemctl enable noodle.service
```

Reboot the machine:
```
[~] systemctl reboot
```
When you SSH back in you can examine the new boot state. You can use the following to examine the target order and when each one became active:
```
[~] systemd-analyze critical-chain
```
You can also use the timestamp values as in the previous examples to confirm that noodle.service and boot.target did indeed start after multi-user.target.

Some other fun commands to get a visual view of dependencies and systemd initialization:
```
# This one creates a dependency graph for a unit in dot format.
[~] systemd-analyze dot <unit name>

# This one outputs and SVG of the initialization sequence.
[~] systemd-analyze plot
```

---
[back to TOC](../README.md)
