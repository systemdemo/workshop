# Dependencies

## Why Do Ordering and Dependencies Matter?

In the days of SysVinit, services were started sequentially at boot based on numbering. Systemd changes this by introducing the concept of dependencies and ordering. Instead of manually numbering your services based on where you think they should run, you can instead list all your dependencies in your unit file. Then systemd can use that information to parallelize start up and shutdown as much as possible. No more manual numbering!

## Ordering

You can order units in 2 ways: with `Before=` or `After=`. Let's say we have a u1.service with `Before=u2.service`. This tells systemd that when we are starting u1.service and u2.service at the same time, we order u1 before u2. We can also do this the other way with `After=` if we have a u2.service with `After=u1.service`.

Let's try it out. We provided 2 units: dinosaur.service and human.service. These are the contents:

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

The basic unit dependency properties in systemd are `Wants=` and `Requires=`.

Let's say we have a u1.service with `Wants=u2.service`. This tells systemd that when we are starting u1.service, we will also start u2.service. However whether u2.service starts successfully or not does not affect whether u1.service will successfully start. If `Before=` or `After=` are not provided, the units will start at roughly the same time. You will want to use `Wants=` for most dependencies.

Let's see this in action. We provided 2 units: dog.service and bone.service. Here are the contents:

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
ExecStart=/bin/false
```

So dog.service *wants* bone.service. However, we are making bone.service return /bin/false so that the service will be considered "failed". We will demonstrate that this does not block dog.service from running successfully:

```
[~] systemctl start dog.service
[~] systemctl status dog.service
[~] systemctl status bone.service
```

Notice how starting dog.service also started bone.service. Also notice how dog.service successfully ran and echoed "woof", while bone.service failed.


`Requires=` is the stricter version of `Wants=` when combined with `After=`. With `Wants=` it does not matter if the wanted dependency starts successfully or not. But with `Requires=` and `After=`, if the required dependency fails to start, then our own unit will also fail to start.

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

life.service... ran? Successfully??? Why!? We should see that water.service failed, but life.service ran successfully. We should have expected to life.service to fail!


The devil is in the details: the wording is very clear that `Wants=` and `Requires=` only refers to *starting* the unit. If you look closely at the logs for water.service, you will see that it did indeed *start* successfully, but the main process returned non-zero (failed). We can rework water.service to make it "fail to start" like so:

```
[~] systemctl edit water.service

# Add the following lines, save and exit
[Service]
Type=exec
```

What this does is tell systemd to wait until we exec into the main service binary before starting other units. In the default type, `Type=simple`, systemd only waits for the unit for fork before considering the unit "started". If you try it again, we should get a dependency error:

```
[~] systemctl start life.service
[~] systemctl status life.service
[~] systemctl status water.service
```

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

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)
