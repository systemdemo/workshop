# systemd for developers

This section provides insights into working programmatically with systemd. This section is particularly relevant for software developers and system administrators who wish to interact with the system using high-level languages like Python.

The section covers various aspects of systemd, including a bit of its architecture, system and service management capabilities, and its API (D-Bus) for programmatically interacting with systemd services. It also provides detailed information on systemd unit files, which are used to define system services and specify their dependencies.

By understanding the fundamentals of systemd and its APIs, developers can gain better control over their Linux-based applications and streamline their deployment and management processes.

# D-Bus

From Lennart Poettering's [blog post](https://0pointer.net/blog/the-new-sd-bus-api-of-systemd.html) about D-Bus in systemd:

>  it's a powerful, generic IPC system for Linux and other operating systems. It knows concepts like buses, objects, interfaces, methods, signals, properties. It provides you with fine-grained access control, a rich type system, discoverability, introspection, monitoring, reliable multicasting, service activation, file descriptor passing, and more.

and why use D-Bus

> in short: D-Bus is great. If you hack on a Linux project and need a local IPC, it should be your first choice. Not only because D-Bus is well designed, but also because there aren't many alternatives that can cover similar functionality.

Since systemd v221, you can use D-Bus to interact with systemd almost fully.

## Intearcating with D-Bus

open a terminal and type:

```
[~] busctl
```
```
NAME                             PID PROCESS         USER            CONNECTION    UNIT                     SESSION>
:1.0                             610 systemd-oomd    systemd-oom     :1.0          systemd-oomd.service     -      >
:1.1                             611 systemd-resolve systemd-resolve :1.1          systemd-resolved.service -      >
:1.13                            895 systemd         vagrant         :1.13         user@1000.service        -      >
:1.2                               1 systemd         root            :1.2          init.scope               -      >
:1.3                             623 systemd-logind  root            :1.3          systemd-logind.service   -      >
:1.4                             632 dbus-broker-lau root            :1.4          dbus-broker.service      -      >
:1.5                             666 NetworkManager  root            :1.5          NetworkManager.service   -      >
:1.6277                        17445 busctl          root            :1.6277       session-3.scope          3      >
:1.9                             831 VBoxService     root            :1.9          vboxadd-service.service  -      >
org.bluez                          - -               -               (activatable) -                        -      >
org.freedesktop.DBus               1 systemd         root            -             init.scope               -      >
org.freedesktop.NetworkManager   666 NetworkManager  root            :1.5          NetworkManager.service   -      >
org.freedesktop.PolicyKit1         - -               -               (activatable) -                        -      >
org.freedesktop.UDisks2            - -               -               (activatable) -                        -      >
org.freedesktop.fwupd              - -               -               (activatable) -                        -      >
org.freedesktop.home1              - -               -               (activatable) -                        -      >
org.freedesktop.hostname1          - -               -               (activatable) -                        -      >
org.freedesktop.locale1            - -               -               (activatable) -                        -      >
org.freedesktop.login1           623 systemd-logind  root            :1.3          systemd-logind.service   -      >
org.freedesktop.network1           - -               -               (activatable) -                        -      >
org.freedesktop.nm_dispatcher      - -               -               (activatable) -                        -      >
org.freedesktop.nm_priv_helper     - -               -               (activatable) -                        -      >
org.freedesktop.oom1             610 systemd-oomd    systemd-oom     :1.0          systemd-oomd.service     -      >
org.freedesktop.portable1          - -               -               (activatable) -                        -      >
org.freedesktop.resolve1         611 systemd-resolve systemd-resolve :1.1          systemd-resolved.service -      >
org.freedesktop.systemd1           1 systemd         root            :1.2          init.scope               -      >
org.freedesktop.timedate1          - -               -               (activatable) -                        -      >
org.freedesktop.timesync1          - -               -               (activatable) -                        -      >
```

These are unique peers and services that are connected to D-Bus. You see two kinds: "numbers" (peers) and "names" (services). If you pay attention, you'll see the `busctl` process connected from `session-3.scope`... that was you! You are a peer.

Just like DNS names, objects can be given names, they act as distinctive, well-known identifiers, rather than being identified by a peer number.

> Exercise: Why do not all services have a connection column? For instance, `org.freedesktop.hostname1` does not seem to have a connection number, while `org.freedesktop.systemd` seems to have one.


## Exploring a service

Lets explore `org.freedesktop.systemd1` tree by executing

```
busctl tree org.freedesktop.systemd1
```

```
└─/org
  └─/org/freedesktop
    ├─/org/freedesktop/LogControl1
    └─/org/freedesktop/systemd1
      ├─/org/freedesktop/systemd1/job
      │ └─/org/freedesktop/systemd1/job/115791
      └─/org/freedesktop/systemd1/unit
        ├─/org/freedesktop/systemd1/unit/NetworkManager_2dwait_2donline_2eservice
        ├─/org/freedesktop/systemd1/unit/NetworkManager_2eservice
        ├─/org/freedesktop/systemd1/unit/_2d_2emount
        ├─/org/freedesktop/systemd1/unit/_2d_2eslice
        ├─/org/freedesktop/systemd1/unit/archlinux_2dkeyring_2dwkd_2dsync_2eservice
```

You can see a sort of tree structure, starting with org, all the way to particular units, if you did the section systemd 101, then you might have a service called `myfirstservice.service`, you can even look for it in the `/org/freedesktop/systemd1/unit`

```
[root@eth50-1 ~]# busctl tree org.freedesktop.systemd1 | grep myfirstservice
        ├─/org/freedesktop/systemd1/unit/myfirstservice_2eservice

```

Now this looks nice, a unit is exposed as an object over D-Bus, but… can we inspect it?, no you can introspect it!

## Introspect a D-Bus object.

to see hay properties, method, and signal a D-Bus object has, introspect is your best tool.
```bash
busctl introspect  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice
```

```
NAME                                TYPE      SIGNATURE       RESULT/VALUE                             FLAGS
org.freedesktop.DBus.Introspectable interface -               -                                        -
.Introspect                         method    -               s                                        -

org.freedesktop.DBus.Peer           interface -               -                                        -
.GetMachineId                       method    -               s                                        -
.Ping                               method    -               -                                        -

org.freedesktop.DBus.Properties     interface -               -                                        -
.Get                                method    ss              v                                        -
.GetAll                             method    s               a{sv}                                    -
.Set                                method    ssv             -                                        -
.PropertiesChanged                  signal    sa{sv}as        -                                        -

org.freedesktop.systemd1.Service    interface -               -                                        -
.AttachProcesses                    method    sau             -                                        -
.BindMount                          method    ssbb            -                                        -
.GetProcesses                       method    -               a(sus)                                   -
.MountImage                         method    ssbba(ss)       -                                        -
…

org.freedesktop.systemd1.Unit       interface -               -                                        -
.Clean                              method    as              -                                        -
.Kill                               method    si              -                                        -
.ReloadOrRestart                    method    s               o                                        -
.ReloadOrTryRestart                 method    s               o                                        -
.ResetFailed                        method    -               -                                        -
.Restart                            method    s               o                                        -
.Start                              method    s               o                                        -
.Stop                               method    s               o
.ActiveEnterTimestamp               property  t               1677186025560576                         emits-change
.ActiveEnterTimestampMonotonic      property  t               70514710280                              emits-change
.ActiveExitTimestamp                property  t               0                                        emits-change
.ActiveExitTimestampMonotonic       property  t               0                                        emits-change
.ActiveState                        property  s               "active"                                 emits-change
.After                              property  as              4 "basic.target" "sysinit.target" "syst… const
.AllowIsolate                       property  b               false                                    const
.AssertResult                       property  b               true                                     emits-change
```


This view is actually quite interesting; it gives you a full overview of what the D-Bus object is and can do. **Be warned that this sits dangerously between "API exposed to be used" and "implementation detail"**, so tread lightly.

There are a few things to explain here, but before we do, let's get the `MainPID` of this unit (if it's running) in a couple of different ways, and let's explain each.

```bash
# gets the MainPID directly by using `get-property`
busctl get-property  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.systemd1.Service MainPID
```
```
u 17822
```

```bash
# gets the MainPID by calling the `Get` method in the org.`freedesktop.DBus.Properties` interface
busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.DBus.Properties  Get ss org.freedesktop.systemd1.Service MainPID
```
```
v u 17822
```

Both of these commands retrieve the `MainPID` property of the service unit `myfirstservice.service`, but:

* The first command, `busctl get-property org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice org.freedesktop.systemd1.Service MainPID`, does it by retrieving the value of the MainPID property directly from the org.freedesktop.systemd1 service using the org.freedesktop.systemd1.Service interface for the myfirstservice.service unit. This command does not require any additional parameters and returns the value of MainPID property as an integer.

* The second command, `busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice org.freedesktop.DBus.Properties Get ss org.freedesktop.systemd1.Service MainPID`, also uses the `busctl` tool to retrieve the `MainPID` property of the `myfirstservice.service` unit. However, it does it indirectly, by calling the method `Get` implemented in the interface `org.freedesktop.DBus.Properties`, and passing the interface and method we want to get as arguments. This command returns the value of `MainPID` as a variant type, and we need to specify that we want it returned as an integer.



This kind of shows you the main operations you can do in D-Bus… you can call methods/set properties/get properties of interfaces. These 3 things can be used to interact with systemd. For instance, let’s restart this unit.


```bash
busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.systemd1.Unit Restart s "replace"
```
```
o "/org/freedesktop/systemd1/job/122357"
```

The answer that systemd gives us is of type `o` (a Path) and it's a job. These jobs are quick, so you can't really see one unless you are monitoring the bus. For instance, if you do:

```
[root@eth50-1 ~]# busctl introspect  org.freedesktop.systemd1 /org/freedesktop/systemd1/job/122749
Failed to introspect object /org/freedesktop/systemd1/job/122749 of service org.freedesktop.systemd1: Unknown object '/org/freedesktop/systemd1/job/122749'.
```

You'll see there is no object, but of you chanin them you get to see

```
busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.systemd1.Unit Restart s "replace" | \
  awk '{print $2}' | \
  xargs busctl introspect  org.freedesktop.systemd1
```
```
...
org.freedesktop.systemd1.Job        interface -         -                                        -
.Cancel                             method    -         -                                        -
.GetAfter                           method    -         a(usssoo)                                -
.GetBefore                          method    -         a(usssoo)                                -
.Id                                 property  u         8306                                     const
.JobType                            property  s         "start"                                  const
.State                              property  s         "running"                                emits-change
.Unit                               property  (so)      "myfirstservice.service" "/org/freedesktop/syste… const
```

Now we could also use regular systemd cli to get this, like

```
[root@eth50-1 ~]# systemctl status myfirstservice
● myfirstservice.service
     Loaded: loaded (/etc/systemd/system/myfirstservice.service; disabled; preset: disabled)
     Active: active (running) since Thu 2023-02-23 21:54:42 UTC; 17s ago
   Main PID: 17987 (sleep)
      Tasks: 1 (limit: 1112)
     Memory: 196.0K (max: 10.0M available: 9.8M)
        CPU: 49ms
     CGroup: /system.slice/myfirstservice.service
             └─17987 sleep infinity
```

And now you know how all this is implemented.

## Common interfaces of a D-Bus Object

All of this looks great, but it seems kind of like arcane magic. Where to start?, Can I discover all this interfaces? The answer is yes, with the most common interfaces to D-Bus. Most D-Bus objects have 3 common interfaces that define basic methods that can be accessed by clients. They are:


* `org.freedesktop.DBus.Introspectable`: This interface provides the Introspect method, which returns an XML description of the interfaces, methods, signals, and properties of the object. This interface is typically used by clients to discover the available functionality of the object.
* `org.freedesktop.DBus.Properties`: This interface provides the Get and Set methods to read and write properties of the object. The GetAll method is also available to retrieve all properties of the object at once. This interface is commonly used to query or update object properties.
* `org.freedesktop.DBus.Peer`: This interface provides methods for basic peer-to-peer communication. It includes the Ping and GetMachineId methods, which can be used to check if the peer is alive and retrieve its unique machine ID.


Lets see one. `org.freedesktop.DBus.Introspectable`

```
busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.DBus.Introspectable Introspect | xq
```

You can probably see near the end

```xml
<method name="\&quot;Clean\&quot;">\n
      <arg type="\&quot;as\&quot;" name="\&quot;mask\&quot;" direction="\&quot;in\&quot;/"/>\n  </method>\n
```

There is method call Clean. This is the building block of interacting with systemd programatically.

## One more detour of D-Bus before continuing, monitor.

You can actually snif whats goes "on the bus". run:

```
busctl monitor org.freedesktop.systemd1
```


This will sniff the traffic going on the bus for org.freedesktop.systemd1 (that's most D-Bus traffic to be honest). Now, on another terminal, execute the command `systemctl start myfirstservice` and see the information flow.

If this looks a lot like pcap for Wireshark, it's because it is. You can actually capture this as pcap and then open it in Wireshark or tshark.


```
busctl capture  org.freedesktop.systemd1 | tshark -r - -Y 'dbus.path ~ "myfirstservice_2eservice"'
```

Then restart myfirstservice with `systemctl start myfirstservice` , The -Y is a pcap capture filter for [D-Bus](https://www.wireshark.org/docs/dfref/d/dbus.html) that just capture changes to `myfirstservice_2eservice`, try removing the filter and reruning tshark.

Now, if you have wireshark installed on your laptop, you can store the output in a `.pcap` file and inspect it in your laptop


```
mkdir -p /opt/conf/spool/ ; busctl capture  org.freedesktop.systemd1  > /opt/conf/spool/mycap.pcap
```

Then restart myfirstservice with `systemctl start myfirstservice` and hit CTL-C in the capture, and open it in your laptop with an UI.

> Exercise: remeber the 2 ways you have to get the MainPID property... are they really 2 ways? or they just one?... see how they are implemented by using

# Interacting with systemd programmatically.

Finally, after all that D-Bus talk, we get to actually interact with systemd programmatically.

As we have mentioned, if you can speak D-Bus, you can talk to systemd, and your favorite language probably has a great D-Bus library that you can use. But good news! Systemd comes with its own D-Bus library, ready for you to use: [`sd-bus.h`](https://github.com/systemd/systemd/blob/main/src/systemd/sd-bus.h). If you can bind to that library, you should.

In Python, we have created a library called [`pystemd`](https://github.com/systemd/pystemd), that provides simple and intuitive access to systemd using the native `sd-bus.h` library. It provides low-level constructs (mimicking, in many cases, the actual C-API) and provides high-level constructs to do more!

Let's spend some time in this library.


## pystemd SDObject

pystemd has a basic `SDObject` that you can use to talk to systemd. There are better abstractions in pystemd, but this one is the basic one. Let's use it to do exactly the same as before. Fire up our custom IPython shell with.

```bash
[~] pystemd-shell
```

Go ahead and import pystemd. Please notice that this shell already has pystemd imported (as well as other pystemd sub-libraries), but still, we should at least try.

```python
In [1]: import pystemd
```

Now lets load the `MainPID`, using `pystemd.base.SDObject`:

```
In [2]: service_path = pystemd.dbuslib.path_encode(b"/org/freedesktop/systemd1/unit", b"myfirstservice.service")

In [3]: sdobject = pystemd.base.SDObject("org.freedesktop.systemd1", service_path)
```

On its own `SDObject` is a empty shell, just waiting to be loaded, go ahead and call the `load` (Later we will see some other alternatives) method

```
In [4]: sdobject.load()

In [5]: sdobject.Service.MainPID
Out[5]: 17987

In [6]: sdobject.Properties.Get('org.freedesktop.systemd1.Service', "MainPID")
Out[6]: 17987

In [7]: type(_)
Out[7]: int
```

`SDObject` takes 2 arguments, the object  "org.freedesktop.systemd1" and the path, in this case `/org/freedesktop/systemd1/unit/myfirstservice_2eservice`, since we dont expect people to remember how to encode a path, we provide a very comfy encoding option `pystemd.dbuslib.path_encode(b"/org/freedesktop/systemd1/unit", b"myfirstservice.service")`

`SDObject` (and the other object we will talk about) will construct themself, this means, they will call the introspect method and then just add Interfaces and methods to the main class, but you need to load it. You have 3 ways of loading the object, calling the load method, using the _autoload method in the constructor, or using a context manager.

In this example we used `sdobject.load()`, but we could as easily just created the object passing the `_autoload=True` to the constructor

```python
In [9]: sdobject = pystemd.base.SDObject("org.freedesktop.systemd1", service_path, _autoload=True)

In [10]: sdobject.Service.MainPID
Out[10]: 17987

```

Or using a contextmanager

```python
In [11]: with pystemd.base.SDObject("org.freedesktop.systemd1", service_path, _autoload=True) as sdobject:
    ...:     print(sdobject.Service.MainPID)
    ...:
17987
```

Using `<tab>` you can autocomplete and see that SDObject has a `Service` and `Unit`

```python
In [17]: sdobject.Service
Out[17]: <b'org.freedesktop.systemd1.Service' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>

In [18]: sdobject.Unit
Out[18]: <b'org.freedesktop.systemd1.Unit' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>
```

And as you can see they correspond to `org.freedesktop.systemd1.Service` and `org.freedesktop.systemd1.Unit` that we knew existed from our introspection. Each method under `org.freedesktop.systemd1.<foo>` becomes a function under `sdobject.<foo>`, same as properties under `org.freedesktop.systemd1.<foo>` becomes a property under `sdobject.<foo>`. The reason for this is that the SDObject we created had a `org.freedesktop.systemd1` object as its base.

Despite this, there is also `Properties` from `org.freedesktop.DBus.Properties`, even tho `org.freedesktop.DBus` is not in the same tree as `org.freedesktop.systemd1`.

```python
In [22]: sdobject.Properties
Out[22]: <b'org.freedesktop.DBus.Properties' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>

```

Other interfaces are not lost, but they are just not directly available, you can get the `_interfaces`

```python
In [23]: sdobject._interfaces
Out[23]:
{'org.freedesktop.DBus.Peer': <b'org.freedesktop.DBus.Peer' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>,
 'org.freedesktop.DBus.Introspectable': <b'org.freedesktop.DBus.Introspectable' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>,
 'org.freedesktop.DBus.Properties': <b'org.freedesktop.DBus.Properties' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>,
 'org.freedesktop.systemd1.Service': <b'org.freedesktop.systemd1.Service' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>,
 'org.freedesktop.systemd1.Unit': <b'org.freedesktop.systemd1.Unit' of /org/freedesktop/systemd1/unit/myfirstservice_2eservice>}

In [24]: sdobject._interfaces['org.freedesktop.DBus.Peer'].GetMachineId()
Out[24]: b'6768d054190f4e778a3ae268f1acfdbd'
```

## Specific unit files as Unit.

Well chances are that you will Interact with units a lot, when we created pystemd, we needed a way to interact with the service manager programmatically, so we created 2 base helpers, [`pystemd.systemd1.Unit`](https://github.com/systemd/pystemd/blob/main/pystemd/systemd1/unit.py) and [`pystemd.systemd1.Manager`](https://github.com/systemd/pystemd/blob/main/pystemd/systemd1/manager.py)… lets explore them a bit


```python
In [32]: sdunit = pystemd.systemd1.Unit("myfirstservice.service", _autoload=True)

In [33]: sdunit.Service.MainPID
Out[33]: 17987

In [34]: sdunit.Unit.Restart("replace")
Out[34]: b'/org/freedesktop/systemd1/job/147350'

```

Just make it easier to call units, by not having to specify all those pesky constants, or encode the path. Other than that, it works exactly the same as SDObject

```python
In [35]: sdmanager = pystemd.systemd1.Manager(_autoload=True)
In [36]: sdmanager.Manager
Out[36]: <b'org.freedesktop.systemd1.Manager' of /org/freedesktop/systemd1>

```

You can now intact with the manager, There is a bunch of interesting features, we could talk about a few

### Get the current unit

```python
In [39]: import os

In [40]: sdmanager.Manager.GetUnitByPID(os.getpid())
Out[40]: b'/org/freedesktop/systemd1/unit/session_2d3_2escope'

In [41]: sdpath = _

In [42]: pystemd.dbuslib.path_decode(sdpath, b"/org/freedesktop/systemd1/unit")
Out[42]: b'session-3.scope'

```

Get process from a unit

```python
In [46]: sdmanager.Manager.GetUnitProcesses(b'session-3.scope')
Out[46]:
[(b'/user.slice/user-1000.slice/session-3.scope',
  4564,
  b'"sshd: vagrant [priv]"'),
 (b'/user.slice/user-1000.slice/session-3.scope',
  4567,
  b'"sshd: vagrant@pts/0"'),
 (b'/user.slice/user-1000.slice/session-3.scope', 4568, b'sudo su -'),
 (b'/user.slice/user-1000.slice/session-3.scope', 4589, b'su -'),
 (b'/user.slice/user-1000.slice/session-3.scope', 4590, b'-bash'),
 (b'/user.slice/user-1000.slice/session-3.scope', 5523, b'tmux'),
 (b'/user.slice/user-1000.slice/session-3.scope', 5525, b'tmux'),
 (b'/user.slice/user-1000.slice/session-3.scope', 5526, b'-bash'),
 (b'/user.slice/user-1000.slice/session-3.scope', 5527, b'-bash'),
 (b'/user.slice/user-1000.slice/session-3.scope', 5565, b'-bash'),
 (b'/user.slice/user-1000.slice/session-3.scope', 13100, b'-bash'),
 (b'/user.slice/user-1000.slice/session-3.scope',
  18922,
  b'/usr/bin/python3 /usr/bin/ipython')]

```

Now let's do a "fun thing" and move our process from the current unit (`session-3.scope`) to `myfirstservice.service`. The only way to do this is to set the `Delegate` property on the service. Let's edit the service unit to have the `Delegate` property set to `True`.


```ini
[~] systemctl edit myfirstservice
…
[Service]
Delegate=true
```

Then lets go back to out python shell and

```python
In [52]: sdmanager.Manager.AttachProcessesToUnit("myfirstservice.service", "/", [os.getpid()])

In [53]: sdmanager.Manager.GetUnitByPID(os.getpid())
Out[53]: b'/org/freedesktop/systemd1/unit/myfirstservice_2eservice'

```
Now you see that the effect this has is that the current process now belongs to the unit `myfirstservice.service`, this is kind of cool, because 2 things… 1) any cgroup property (like restricting the memory limit) its applied to the current process and 2) stopping myfirstservice.service will stop this process… lets put this theory to the tests.

```python
In [54]: sdmanager.Manager.StopUnit("myfirstservice.service", "replace")
Terminated
[root@eth50-1 ~]
```

more on this, when we review `pystemd.futures`.


## Transient units with pystemd.run

Same as `systemd-run`, which is a command-line tool provided by systemd for running transient units, `pystemd` comes with `pystemd.run`. It allows you to easily create and manage short-lived units and services from the command line.

The method `pystemd.run` is a spiritual child of `systemd-run` and `subprocess.run`. That is, it takes a more API-driven approach than `systemd-run`, but it's not a drop-in replacement for `subprocess.run` (yet!).


You can use it very simple

```bash
[root@eth50-1 ~]# pystemd-shell
```
```python
In [1]: import pystemd.run

In [2]: pystemd.run(["/usr/bin/sleep", "infinity"])
Out[2]: <pystemd.systemd1.unit.Unit at 0x7ff26c2207d0>

In [3]: unit = _

In [4]: unit.Service.MainPID
Out[4]: 20478

In [5]: unit.Service.GetProcesses()
Out[5]:
[(b'/system.slice/pystemdf3db2ea8c208497b8e557148265783a2.service',
  20478,
  b'/usr/bin/sleep infinity')]

In [7]: unit.Unit.Id
Out[7]: b'pystemdf3db2ea8c208497b8e557148265783a2.service'

```

if you take the Id of the unit, then you can see the status, and the generated file with

```yaml
[~] systemctl status pystemdf3db2ea8c208497b8e557148265783a2.service
● pystemdf3db2ea8c208497b8e557148265783a2.service - pystemd: pystemdf3db2ea8c208497b8e557148265783a2.service
     Loaded: loaded (/run/systemd/transient/pystemdf3db2ea8c208497b8e557148265783a2.service; transient)
  Transient: yes
     Active: active (running) since Fri 2023-02-24 17:10:54 UTC; 2min 55s ago
   Main PID: 20478 (sleep)
      Tasks: 1 (limit: 1112)
     Memory: 196.0K
        CPU: 1ms
     CGroup: /system.slice/pystemdf3db2ea8c208497b8e557148265783a2.service
             └─20478 /usr/bin/sleep infinity

Feb 24 17:10:54 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: Started pystemdf3db2ea8c208497b8e557148265783a2.service - pystemd: pystemdf3db2ea8c208497b8e5571>

```

```ini
[~] systemctl cat  pystemdf3db2ea8c208497b8e557148265783a2.service
# /run/systemd/transient/pystemdf3db2ea8c208497b8e557148265783a2.service
# This is a transient unit file, created programmatically via the systemd API. Do not edit.
[Unit]
Description=pystemd: pystemdf3db2ea8c208497b8e557148265783a2.service

[Service]
ExecStart=
ExecStart="/usr/bin/sleep" "infinity"
RemainAfterExit=no
```

Go ahead and stop either with python `unit.Stop(b"replace")` or with `systemctl stop pystemdf3db2ea8c208497b8e557148265783a2.service`

### shells, redirecting stdin/out and extras

same as systemd-run, you can do some pty magic and get the output on your terminal

```python
In [17]: import sys

In [18]: pystemd.run(
    ["/usr/bin/env"],
    stdout=sys.stdout,
    wait=True,
    env={"FOO": "bar"}
)
```
```ini
LANG=en_US.UTF-8
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
WORKSHOP_DIR=/opt/workshop
INVOCATION_ID=8f7f00f021f84afdb4c9d7a6c4f9f446
SYSTEMD_EXEC_PID=20544
FOO=bar
```

```python
In [19]: pystemd.run(
    ["/usr/bin/bash"],
    stdin=sys.stdin,
    stderr=sys.stderr,
    stdout=sys.stdout,
    pty=True,
    wait=True,
    env={"FOO": "bar"}
)
```
```yaml
[~] systemctl status $$
● pystemd8ae31f1d98be4a8abdb34e7570990eb8.service - pystemd: pystemd8ae31f1d98be4a8abdb34e7570990eb8.service
     Loaded: loaded (/run/systemd/transient/pystemd8ae31f1d98be4a8abdb34e7570990eb8.service; transient)
  Transient: yes
     Active: active (running) since Fri 2023-02-24 17:24:02 UTC; 10s ago
   Main PID: 20553 (bash)
      Tasks: 3 (limit: 1112)
     Memory: 5.6M
        CPU: 50ms
     CGroup: /system.slice/pystemd8ae31f1d98be4a8abdb34e7570990eb8.service
             ├─20553 /usr/bin/bash
             ├─20576 systemctl status 20553
             └─20577 less

Feb 24 17:24:02 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: Started pystemd8ae31f1d98be4a8abdb34e7570990eb8.service - pystemd: pystemd8ae31f1d98be4a8abdb34e>
```

```
unit = pystemd.run("/usr/bin/stress --cpu 1", extra={"CPUQuota": 0.5})
```


You may add almost all properties of a service to a transient service and it should work, for instance the following example will run stress on a unit that can only use 10% of the cpu, (if you want on another terminal, or on your tmux session, you might want to start htop).


```python
In [24]: unit = pystemd.run("/usr/bin/stress --cpu 2", extra={"CPUQuota": 0.1})

In [25]: unit.Stop(b"replace")
Out[25]: b'/org/freedesktop/systemd1/job/166884'

```

Some extra examples you might want to try (just type them in the pystemd-shell):

* **dynamic_user_socal** : Creates a unit using a dynamically generated user.
* **directories_socal** : A bunch of directory-fu
* **ip_user_socal**: Using BPF filters to limit network access.


We will see more of `pystemd.run` on the service and sandboxing deepdive, so let's not spend too much time here.

## Futures with pystemd.future

A new addition to `pystemd` that we are super excited about is `pystemd.futures`. It expands on the ideas of Python's `concurrent.futures`, but applies a dash of systemd on top of that.

What if you could take parts of your code (don't exec, just fork) and run them on a different systemd unit? That way, you might have parts of your code that do not have access to the network or that have CPU restrictions, or that can't write to disk or better yet, that you can actually kill. There are three implementations of this feature that we can study.



### pystemd.future.run

The first one is call `pystemd.futures.run`, and its just a convinient wrapper to run a method or function inside another systemd unit.

We have a function written that just waste cpu for a particular timeout, you can view it with

```python
[~] pystemd-shell

In [1]: ppcode cpu_waste

>>> # /root/.local/bin/pystemd-shell[306:310]

def cpu_waste(timeout):
    t0= time.time()
    while time.time() - t0 < timeout:
        2**64 -1

    return 2**64 -1
```

If you execute `cpu_waste(5)`, and monitor htop, you will see the spike to 100% of cpu for 5 seconds.

We can use pystemd.futures.run to execute it in a different systemd context, you can do:

```python
In [2]: pystemd.futures.run(cpu_waste, {"CPUQuota": 0.1, "User": "nobody"}, 60)
```

And run the stress test for 60 seconds, then you can go to to htop and get

```
22077 nobody      20   0  319M 76068  4844 R  10.9  7.7  0:00.91 /usr/bin/python3 /root/.local/bin/pystemd-shell
```

The process is now run as `nobody` and the cpu is ~10% … you can also do `systemctl status 22077` (where 22077 is the pid of the process), and that is effectively another unit


### pystemd.futures.TransientUnitPoolExecutor

Same as ProcessPoolExecutor, where you can shard and ratelimit work on consumers, you have `pystemd.futures.TransientUnitPoolExecutor`, that can be used as the example in [examples/future_cpucap_pool.py](https://github.com/systemd/pystemd/blob/main/examples/future_cpucap_pool.py). You can view the usage in our shell:

```python
In [2]: ppcode future_cpucap_pool.main
>>> # /opt/pystemd/examples/future_cpucap_pool.py[51:65]

def main(cpu_quota=0.25):
    with TransientUnitPoolExecutor(
        properties={"CPUQuota": cpu_quota, "User": "nobody"},
        max_workers=10,
    ) as poold:
        top = MyTop(poold.unit)
        top.start()

        poold.submit(run, 5)
        poold.submit(run, 10)
        poold.submit(run, 15)
        poold.submit(run, 20)
        poold.submit(run, 25)
        poold.submit(run, 30)
```

This will start a Pool of workers that will consume work… the work is defined in `run` (feel free to see the code with `ppcode future_cpucap_pool.run`, but it’s exactly the same as cpu_waste) and we execute this job to be executed in the pool. The Pool has a quota and its running as nobody, as added bonus it will print the cpu usage

```python
In [4]: future_cpucap_pool.main()
```


### pystemd.futures.TransientUnitProcess

There is also another api in python in multiprocessing that use the Process object (a base object for the concurrent.future if i may add), that you can actually swap for pystemd.futures.TransientUnitProcess , there is an example in [examples/future_cpucap_process.py](https://github.com/systemd/pystemd/blob/main/examples/future_cpucap_process.py) that you can follow.

You define a process by subclassing TransientUnitProcess, and adding a run method.

```python
In [10]: ppcode future_cpucap_process.Process
-------> ppcode(future_cpucap_process.Process)
>>> # /opt/pystemd/examples/future_cpucap_process.py[10:22]

class Process(TransientUnitProcess):
    def __init__(self, timeout, properties):
        self.timeout = timeout
        super().__init__(properties=properties)

    def run(self):
        """
        This is suppose to waste a bunch of CPU.
        """
        t0 = time.time()
        while time.time() - t0 < self.timeout:
            2**64 - 1
```

Then you might as well just use it

```python
In [11]: ppcode future_cpucap_process.main
-------> ppcode(future_cpucap_process.main)
>>> # /opt/pystemd/examples/future_cpucap_process.py[24:35]

def main(cpu_quota=0.2):

    p = Process(timeout=30, properties={"CPUQuota": cpu_quota, "User": "nobody"})
    p.start()
    process = psutil.Process(p.pid)

    while p.is_alive():
        with suppress(NoSuchProcess):  # the process can die mid check
            cpu_percent = process.cpu_percent(interval=1)
            sys.stdout.write("\033[2J\033[1;1H")
            print(f"current {cpu_percent=}")



In [12]: future_cpucap_process.main
-------> future_cpucap_process.main()
current cpu_percent=21.8
```

This respects the contract you have with Process  where you can just get `TransientUnitProcess.is_alive()` to check if the process is alive. `TransientUnitProcess.wait()` and `TransientUnitProcess.join()` is still supported

# pystemd daemon

Now it's time to have fun using the daemon. For this demo, it will be useful if we have divided screens, as it makes it simple to see the changes. The simple way is to start `tmux`, then hit `CTRL-b`, followed by the double quotes (").

On one part of the screen, do `watch systemctl status daemon-demo-service.service`, and in the other, open your `pystemd-shell` and execute `daemon_demo_service`. If that's a bit hard to follow, this section comes with a quick helper. Just execute it on your fresh terminal:


```
[~] daemon-demo
```

You can see from the status window that the process is in the activating state.


```yaml
● pystemd-name-server.service - pystemd: pystemd-name-server.service
     Loaded: loaded (/run/systemd/transient/pystemd-name-server.service; transient)
  Transient: yes
     Active: activating (start) since Fri 2023-02-24 23:06:01 UTC; 44s ago
   Main PID: 23783 (python3)
      Tasks: 3 (limit: 1112)
     Memory: 49.3M
        CPU: 601ms
     CGroup: /system.slice/pystemd-name-server.service
             └─23783 /usr/bin/python3 /root/.local/bin/pystemd-shell
```

We have 5 minutes to activate the service, so lets have some fun, lets add some text. from the python console:


```
In [1]: pystemd.daemon.notify(False, status="procastinating")
Out[1]: 1

```

Now systemctl status shows a new status message

```

● pystemd-name-server.service - pystemd: pystemd-name-server.service
     Loaded: loaded (/run/systemd/transient/daemon-demo-service.service; transient)
  Transient: yes
     Active: activating (start) since Fri 2023-02-24 23:10:15 UTC; 1min 14s ago
   Main PID: 23849 (python3)
     Status: "procastinating"
      Tasks: 3 (limit: 1112)
     Memory: 49.9M
        CPU: 841ms
     CGroup: /system.slice/pystemd-name-server.service
             └─23849 /usr/bin/python3 /root/.local/bin/pystemd-shell
```


How is this possible? Let's see the unit by using `cat` on the unit file...


```
In [2]: cat /run/systemd/transient/daemon-demo-service.service
# This is a transient unit file, created programmatically via the systemd API. Do not edit.
[Service]
StandardInput=tty
StandardOutput=tty
StandardError=tty
TTYPath=/dev/pts/4
Type=notify

[Unit]
Description=pystemd: daemon-demo-service.service

[Service]
ExecStart=
ExecStart="/usr/bin/python3" "/usr/local/src/workshop/bin/pystemd-shell"
RemainAfterExit=no
Environment="UNIT_NAME=daemon-demo-service.service" "TERM=screen-256color"
TimeoutStartSec=5min
WatchdogSec=4min 59s

```

The relevant section for this is `Type=notify`. This sets the unit as a notify unit (which instructs systemd that the unit will send information to it). `TimeoutStartSec=5min` tells systemd that we can take up to 5 minutes to start, and `WatchdogSec=4min 59s` tells systemd that after the unit is activated, the service will send a ping at most after 4 minutes and 59 seconds.

We still have time, so let's see the environmental variables.


```
In [3]: env
Out[3]:
{'DEBIAN_ROOT': '/opt/debian',
 'LANG': 'en_US.UTF-8',
 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin',
 'WORKSHOP_DIR': '/opt/workshop',
 'NOTIFY_SOCKET': '/run/systemd/notify',
 'WATCHDOG_PID': '15298',
 'WATCHDOG_USEC': '299000000',
 'INVOCATION_ID': 'dd6fd487d48c4415a34feaf4a619981e',
 'TERM': 'screen-256color',
 'SYSTEMD_EXEC_PID': '15298',
 'UNIT_NAME': 'daemon-demo-service.service',
 'EDITOR': 'vim'}
```

notice this

```python
...
 'NOTIFY_SOCKET': '/run/systemd/notify',
 'WATCHDOG_PID': '15298',
 'WATCHDOG_USEC': '299000000',
 ...
```

These are the ones that are relevant to what we just discussed. Now we are ready to activate the unit. Let's send a `ready=1` signal.


```python
In [4]: pystemd.daemon.notify(False, status="ok, lets go!!", ready=1)
Out[4]: 1
```

Now you can see that the active state is "active," and the status has changed.

```yaml
     Active: active (running) since Tue 2023-03-07 02:34:23 UTC; 36s ago
     Status: "ok, lets go!!"
...
Mar 07 02:34:23 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: Started daemon-demo-service.service - pystemd: daemon-demo-service.service.

```

Now we need to send watchdog pings, we do this with:

```python
In [6]: pystemd.daemon.notify(False, WATCHDOG=1)
Out[6]: 1
```

> Exercise: How to clear the status text?

If you want to know how many seconds you need to send a ping, you can check the environment variable `WATCHDOG_USEC`, or just run the following command:


```
In [9]: pystemd.daemon.watchdog_enabled()
Out[9]: 299000000
```

this time can be changed at runtime, as

```
pystemd.daemon.notify(False, WATCHDOG=1, WATCHDOG_USEC=pystemd.daemon.watchdog_enabled() / 2 )

```

or turn it off

```
In [23]: pystemd.daemon.notify(False, WATCHDOG=1, WATCHDOG_USEC=0 )
Out[23]: 1
```

> what would happen if we fail to send watchdog ping?


Systemd would send a `SIGABRT`. Our process should either catch and handle it, or we can wait for systemd to kill us. Let's handle this signal.


```
In [24]: import signal
In [26]: signal.signal(signal.SIGABRT, lambda *x: print("time to eventually die", *x) )
Out[26]: <Handlers.SIG_DFL: 0>

# lets reenable watchdog and then
In [27]: while True: pystemd.daemon.notify(False, WATCHDOG=1, WATCHDOG_USEC=1 )
```

Now we are hitting systemd pretty frequently, just hit `Ctrl-C` for us to skip a signal, and then you'll see...


```
time to eventually die 6 <frame at 0x7ff5ceae1340, file '/usr/lib64/python3.11/selectors.py', line 468, code select>
```

We can now check the status has change to:

```
     Active: deactivating (stop-watchdog) (Result: watchdog) since Tue 2023-03-07 02:56:15 UTC; 11s ago
...

Mar 07 02:56:15 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: daemon-demo-service.service: Watchdog timeout (limit 1us)!
Mar 07 02:56:15 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: daemon-demo-service.service: Killing process 17012 (python3) with signal SIGABRT.
```

Sadly there is no coming back from this, we might just exit

```
In [28]: exit()
```

Once you exit, you'll see in the logs

```
Mar 07 02:58:48 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: daemon-demo-service.service: Main process exited, code=dumped, status=6/ABRT
Mar 07 02:58:48 eth50-1.rsw1ah.30.frc4.tfbnw.net systemd[1]: daemon-demo-service.service: Failed with result 'watchdog'.
```

## Lets go back in, change main pid.

We are going to try to tell systemd to track another process (change the MainPID of the unit). Lets first go back in the demo:


```
[~]# /usr/local/src/workshop/bin/pystemd-shell
...

In [1]: daemon_demo_service
...
```

now lets start a new process:

```
In [1]: p = subprocess.Popen(['nohup', 'sleep', 'infinity'])

nohup: ignoring input and appending output to 'nohup.out'
In [2]: pystemd.daemon.notify(False, MainPID=p.pid, watchdog_usec=0, ready=1)
Out[2]: 1

```

We did a lot in one go; we created a process with `nohup` (so it's daemonized), then we 1) set the main PID of the process to that, 2) disabled the watchdog, and 3) marked the unit as ready.

From now on, `pystemd-shell` is no longer the main process of the unit and can't send any more notify messages. This can be changed with the option [`NotifyAccess=exec`](https://www.freedesktop.org/software/systemd/man/systemd.service.html#NotifyAccess=), which allows `pystemd-shell` (a process started by systemd) and `sleep infinity` (the `MainPID` of the service) to send messages to the notify socket.


