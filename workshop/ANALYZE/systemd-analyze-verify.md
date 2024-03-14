# systemd-analyze verify

Some people take the approach of writing their unit files, then running it while hoping that it just works. But did you know there is a systemd tool to do basic validation of your unit file? It's called `systemd-analyze verify <unit name>`. Given a unit name it will validate some common errors such as dependency cycles, typos/missing properties, etc. Let's try it out!

## Detecting cycles

A cycle is when 2 or more units have conflicting dependencies on each other. For example, if soup.service requires ladle.service to run after it, but ladle.service is set up to also require soup.service and run after it. Both services cannot simultaneously run after each other, hence a cycle is created. Let's try this out by creating ladle.service and soup.service as shown below:

```
[~] systemctl edit --force --full soup.service

# paste these contents
[Unit]
After=ladle.service
Requires=ladle.service

[Service]
ExecStart=/bin/echo "yummy soup"

[~] systemctl edit --force --full ladle.service

# paste these contents
[Unit]
After=soup.service
Requires=soup.service

[Service]
ExecStart=/bin/echo "scooper"
```

Now let's detect the cycle:
```
[~] systemd-analyze verify ladle.service
```

You can pass either ladle.service or soup.service to the command. Both will generate an error message that the transaction order is cyclic.

What happens if both of these units are wanted by a target? Let's try editing the units to add the following contents:

```
[Install]
WantedBy=multi-user.target
```

Don't forget to enable the units with `systemctl enable ladle.service soup.service`. Now try to verify again:
```
[~] systemd-analyze verify ladle.service
```

You should see that systemd-analyze detected the cycle, and that systemd deleted a job from the transaction in order to break the cycle! Leaving cycles in your boot up can be problematic so make sure to disable these units after this exercise.

## Typos and improperly configured units

`systemd-analyze verify <unit>` can also do basic linting on your unit files. Try it out now. And example of a bad unit is below:
```
[~] systemctl edit --force --full fulloftypos.service

# contents
[Typo]
ExecStart=echo hi

[Unit]
Meow=hi

[~] systemd-analyze verify ladle.service
```

Notice that for certain cases, systemd will explicitly warning you that it will ignore the issue. And for others, it errors out.

## Missing dependencies

You can also detect if hard dependencies don't exist. Try this example:

```
[~] systemctl edit --force --full missingreq.service

# contents
[Unit]
Requires=ireallydontexist.service

[Service]
ExecStart=echo hi

[~] systemd-analyze verify missingreq.service
```

## Non-executable and missing executables

This example shows that we can also check if an executable doesn't exist:

```
[~] systemctl edit --force --full noexistexec.service

# contents
[Service]
ExecStart=/iamnotexec

[~] systemd-analyze verify noexistexec.service
```

Exercise: Change the `ExecStart=` for noexistexec.service to point to a non-executable file and see what happens when you run `systemd-analyze verify noexistexec.service`.

---
[back to TOC](../README.md)
