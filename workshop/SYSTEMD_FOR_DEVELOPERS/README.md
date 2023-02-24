# systemd for developers

This section provides insights into working programatically with systemd. This section is particularly relevant for software developers and system administrators who with to interact with the system using high level languages like python.

The section covers various aspects of systemd, including  a bit of its architecture, system and service management capabilities, and its API (DBUS) for programmatically interacting with systemd services. It also provides detailed information on systemd unit files, which are used to define system services and specify their dependencies.

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

These are unique peers and services that are connected to D-Bus, you see 2 kinds "numbers" (peers) and "names" (services), if you pay attention you'll see the process `busctl` connected from session-3.scope... that was you!!!, you are a peer.

Things that has names are just like DNS names, they just have a well known name instead of an assigned peer number.

> Exercise: Why not all services have a connection column?, for instance `org.freedesktop.hostname1` does not seems to have a connection number, while `org.freedesktop.systemd` seems to have one


## exploring a service

Lets explore org.freedesktop.systemd1 tree by executing

```
busctl tree org.freedesktop.systemd1
```

```
root@eth50-1 ~]# busctl tree org.freedesktop.systemd1                                                                                                        
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

Now this looks nice… a unit is exposed as an object over D-Bus, but… can we inspect it?, no you can introspect it!

## Introspect a D-Bus object.

to see hay properties, method, and signal a D-Bus object has, introspect is your best tool.
```
[~] busctl introspect  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice
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


This view it's actually quite interesting, it gives you a full overview of what the S-Dbus object is and can do. **Be warn, that this sits dangerously between “api exposed to be used” and “implementation detail”**, tread lightly. 


There is a few things to explain here, but before we do, lets get the MainPID of this unit (if its runing), a couple of diferent ways and lets exaplin each

```
[root@eth50-1 ~]# busctl get-property  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.systemd1.Service MainPID
u 17822


[root@eth50-1 ~]# busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.DBus.Properties  Get ss org.freedesktop.systemd1.Service MainPID
v u 17822

```


Both of these commands retrieve the `MainPID` property of the service unit `myfirstservice.service`, but:

* The first command, `busctl get-property org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice org.freedesktop.systemd1.Service MainPID`, does it by retrieving the value of the MainPID property directly from the org.freedesktop.systemd1 service using the org.freedesktop.systemd1.Service interface for the myfirstservice.service unit. This command does not require any additional parameters and returns the value of MainPID property as an integer.

* The second command, `busctl call org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice org.freedesktop.DBus.Properties Get ss org.freedesktop.systemd1.Service MainPID`, also uses the busctl tool to retrieve the MainPID property of the myfirstservice.service unit. However, it does it indirectly, by calling the method `Get` implemented in the interface  `org.freedesktop.DBus.Properties`, and passing what interface and method we want to get, This command also returns the value of MainPID as an var type, and then specify it to be an integer.


This kind of shows you the main operations you can do in D-Bus… you can call methods/set properties/get properties of interfaces, These 3 things can be used to interact with systemd. For instance, let’s restart this unit.

This kind of shows you the main operations you can do in D-Bus… you can call methods/set properties/get properties of interfaces, These 3 things can be used to interact with systemd. For instance, let’s restart this unit.

```
[root@eth50-1 ~]# busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.systemd1.Unit Restart s "replace"
o "/org/freedesktop/systemd1/job/122357"

```

And then check the runtime with

```
[root@eth50-1 ~]# busctl introspect  org.freedesktop.systemd1 /org/freedesktop/systemd1/job/122749
Failed to introspect object /org/freedesktop/systemd1/job/122749 of service org.freedesktop.systemd1: Unknown object '/org/freedesktop/systemd1/job/122749'.
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

## Common interfaces od D-Bus Object

All this looks great, but seems kind of arcane magic, can i discover all of this… the answer is yes, with the most common interfaces to D-Bus. Most D-Bus objects 3 common interfaces that define basic methods that can be accessed by clients. they are:

* `org.freedesktop.DBus.Introspectable`: This interface provides the Introspect method, which returns an XML description of the interfaces, methods, signals, and properties of the object. This interface is typically used by clients to discover the available functionality of the object.
* `org.freedesktop.DBus.Properties`: This interface provides the Get and Set methods to read and write properties of the object. The GetAll method is also available to retrieve all properties of the object at once. This interface is commonly used to query or update object properties.
* `org.freedesktop.DBus.Peer`: This interface provides methods for basic peer-to-peer communication. It includes the Ping and GetMachineId methods, which can be used to check if the peer is alive and retrieve its unique machine ID.

Lets see one. `org.freedesktop.DBus.Introspectable`

```
[~] busctl call  org.freedesktop.systemd1 /org/freedesktop/systemd1/unit/myfirstservice_2eservice  org.freedesktop.DBus.Introspectable Introspect | xq 
```

you can probably see near the end

```xml
<method name="\&quot;Clean\&quot;">\n   
      <arg type="\&quot;as\&quot;" name="\&quot;mask\&quot;" direction="\&quot;in\&quot;/"/>\n  </method>\n    
```

there is method call Clean. This is the building block of interacting with systemd programatically.

## one more detour of D-Bus before continuing, monitor.

You can actually snif whats goes "on the bus". run:

```
[~] busctl monitor org.freedesktop.systemd1
```


this will sniff the traffic going on teh bus for org.freedesktop.systemd1 (thats most dbus traffic to be honest), now on another terminal do , and see the information flow `systemctl start myfirstservice`

If this looks a lot like pcap for wireshark, it's because it is… you can actually capture this as pcap, and then open it in wireshark or tshark.

```
[~/] busctl capture  org.freedesktop.systemd1 | tshark -r -
```

Then restart myfirstservice with `systemctl start myfirstservice` , you will see a bunch of traffic. Now, if you have wireshark installed on your laptop, you can

```
[root@eth50-1 ~]# mkdir /opt/conf/spool/
[root@eth50-1 ~]# busctl capture  org.freedesktop.systemd1  > /opt/conf/spool/mycap.pcap

```

Then restart myfirstservice with `systemctl start myfirstservice` and hit CTL-C in the capture, and open it in your laptop with an UI.

# Interacting with systemd programmatically.

Finally, after all that D-Bus talk, we get to actually interact with systemd programmatically.


As we have mentioned, if you can speak D-Bus, you can talk to systemd, your favorite language probably has a great D-Bus library that you can use. But good news! Systemd comes with its own D-Bus library, ready for you to use, [sd-bus.h](https://github.com/systemd/systemd/blob/main/src/systemd/sd-bus.h), if you can bind to that library, you should.

In python, we have created a library called [pystemd](https://github.com/systemd/pystemd), that provides simple and intuitive access to systemd using native sd-bus.h. It provides low level constructs (mimicking in many cases the actual C-Api) and provides high level constructs to do more!

Let’s spend some time in this library.

## pystemd SDObject

pystemd has a basic SDObject that you can use to talk to systemd… there are better abstraction in pystemd, but this one is the basic one, lets use it to do exactly the same as before. Fire up an ipython shell

```bash
[root@eth50-1 ~] ipython
Python 3.11.1 (main, Jan  6 2023, 00:00:00) [GCC 12.2.1 20221121 (Red Hat 12.2.1-4)]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.5.0 -- An enhanced Interactive Python. Type '?' for help.
```
```python
In [1]: import pystemd

In [2]: service_path=pystemd.dbuslib.path_encode(b"/org/freedesktop/systemd1/unit", b"myfirstservice.service")

In [3]: sdobject = pystemd.base.SDObject("org.freedesktop.systemd1", service_path)

In [4]: sdobject.load()

In [5]: sdobject.Service.MainPID
Out[5]: 17987

In [6]: sdobject.Properties.Get('org.freedesktop.systemd1.Service', "MainPID")
Out[6]: 17987

In [7]: type(_)
Out[7]: int

```

`SDObject` takes 2 arguments, the object  "org.freedesktop.systemd1" and the path, in this case `/org/freedesktop/systemd1/unit/myfirstservice_2eservice`, since we dont expect people to remember how to encode a path, we provide a very comfy encoding option `pystemd.dbuslib.path_encode(b"/org/freedesktop/systemd1/unit", b"myfirstservice.service")`

SDObject (and the other object we will talk about) will construct themself, this means, they will call the introspect method and then just add Interfaces and methods to the main class, but you need to load it. You have 3 ways of loading the object, calling the load method, using the _autoload method in the constructor, or using a context manager.

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

now, lets do a “fun thing”, and lets move our proces, from the current unit (`session-3.scope'`) to `myfirstservice.service`, the only way that we have to do this, is to set the delegetable property on the service , so let's do that,  and edit the service unit to have the Delegate property to True

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


