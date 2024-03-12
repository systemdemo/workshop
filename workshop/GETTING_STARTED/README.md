# Getting Started


## Initial Steps

To get started with the workshop, you will need a Linux operating system that uses systemd as its default init system. You can use any Linux distribution that uses systemd, such as Ubuntu, Debian, Fedora, CentOS, or Arch Linux. We provide (and recommend using) a Vagrant + Virtual Box setup, that will allow you to run this workshop in not only Linux, but also MacOS and Windows.


To install Vagrant with VirtualBox, follow these steps:

1. Download and install VirtualBox from the official website: https://www.virtualbox.org/wiki/Downloads. Follow the instructions for your operating system.

2. Download and install Vagrant from the official website: https://www.vagrantup.com/downloads. Again, follow the instructions for your operating system.

Once both VirtualBox and Vagrant are installed, open a terminal or command prompt and type the following command to verify that Vagrant is installed correctly:


```bash
vagrant --version
```

You should see the version number of Vagrant printed on the screen.

Then clone this repository to your local machine using the following command:

```bash
git clone https://github.com/systemdemo/workshop.git
```

`cd` into the workshop repo check out and start your machine with `vagrant up`

```bash
[~/ ] cd workshop
[~/workshop ] vagrant up
```

This will take care of downloading a base image and starting a virtual box machine with it. Feel free take a sneak peak at the [Vagrantfile](https://github.com/systemdemo/workshop/blob/main/Vagrantfile) to understand what it's doing.

# Hey I can't run your virtualbox, what now?

## use the cloud
Well, this happens to M1/M2 Mac owners while VirtualBox is still in development for them, but not all hope is lost. You can still provision your own server. All you need is a Fedora 37 virtual machine, which can be on your own machine or on the cloud. So, grab one of those nice free tiers and you can start provisioning. Just follow the instructions below.

WARNING: These instructions are quite intrusive. Please use a new/fresh instance.

```
[root@~] dnf install -y git &&\
    git clone https://github.com/systemdemo/workshop /usr/local/src/workshop &&\
    bash /usr/local/src/workshop/bin/provision-build &&\
    python3 /usr/local/src/workshop/bin/provision-host &&\
    echo "I did it!"
```

If you come to our demo, we might have some Linode micro-instances to share.

## use a container

You can install podman and then run `./workshopctl build` and then subsequent `./workshopctl run`.

# Once the machine is up, what do I do?.

## Access the Virtual Machine

Once the virtual machine is up and running, you can use the `vagrant ssh` command to connect and interact with it.

```bash
[~/workshop ] vagrant ssh
```

This will open a new terminal window with a shell prompt inside the virtual machine.

We have arranged to set up to log in as root. There is a "vagrant" user on the system that we will occasionally use in the demo, but most functions will require you to run as root.

That's it! You have successfully executed your first Vagrant and launched a virtual machine.

## Using tmux

Sometimes it will be useful to have a split panel. For that intent we will use tmux. Here's a quick intro to tmux:

To start tmux, on the terminal window type the following command:

```bash
[~/] tmux
```

This will change the look of the terminal. You can split the screen with `CTL-b` (that's the ctrl key and the b key at the same time) and then use `%` (the percentage symbol, usually that's shift+5) for vertical and " (quotes) horizontal.

You can click each panel to make it focus, and you can scroll up and down using your wheel on the mouse.

## Shutting Down and Recreating the Virtual Machine

Virtual machines on laptops are useful for development, testing, or any other ephemeral and isolation purposes. When you are done, you can just discard them.

To shut down the virtual machine, run the `vagrant halt` command. To delete it entirely, use the `vagrant destroy` command.

## Wireshark?
There is only one example that uses Wireshark. If you have Wireshark installed, great! If you don't, it's probably easy to install, but for just one exercise, it's probably not worth it. It's up to you!

## Configuring Your Environment

If you want to configure your environment to do things like setting the editor (we are going to be editing files and unless you are fine with nano, you might want to change your editor), create a file in `conf/bashrc.local.conf` in the workshop repo, and then re-provision (or destroy and recreate) the virtual machine. Here is an example of what the contents could look like:

```bash
# .bash_profile
# conf/bashrc.local.conf

export EDITOR=$(which vim)

# User specific environment and startup programs
```

Save the contents and then run:


```bash
[~/workshop ] vagrant provision
```

## Environment Prerequisites

Some of the features we will be demoing do not work well when SELinux is set to enforcing mode. The virtual machine we will be using already sets SELinux to permissive mode. You can verify this in the virtual machine by running:

```bash
[~] getenforce
```

If `getenforce` says you are in enforcing mode, you can set it to permissive by running:

```bash
[~] setenforce Permissive
```

---
[back to TOC](../README.md)
