# Dependencies

## Why Do Dependencies and Ordering Matter?

In the days of SysVinit, services were started sequentially at boot based on numbering. Systemd changes this by introducing the concept of dependencies and ordering. Instead of manually numbering your services based on where you think they should run, you can instead list all your dependencies in your unit file. Then systemd can use that information to parallelize start up and shutdown as much as possible. No more manual numbering!

## Dependencies

Requires=
Wants=

## Ordering

Before=
After=

## Install

< talk about targets, enable, disable things >

## Fancy Stuff

PartOf=
BindsTo=
Conflicts=

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)
