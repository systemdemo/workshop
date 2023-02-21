# Getting Started

## Initial steps

To get started with the workshop, you will need a Linux operating system that uses systemd as its default init system. You can use any Linux distribution that uses systemd, such as Ubuntu, Debian, Fedora, CentOS, or Arch Linux. We provide (and recommend using) a Vagrant + Virtual Box setup, that will “allow” you to run this workshop in not only linux, but also macos and windows.


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

cd into the workshop repo directory and start your machine with `vagrant up`

```bash
[~/ ] cd workshop
[~/workshop ] vagrant up
```

This will take care of downloading a base image and starting a virtual box machine with it, feel free take a sneak peak at the [Vagrantfile](https://github.com/systemdemo/workshop/blob/main/Vagrantfile) to understand what exactly you are doing.

# Once the machine is up, what to do?.

## Access the virtual machine.

Once the virtual machine is up and running, you can use the vagrant ssh command to connect to it and interact with it.

```bash
[~/workshop ] vagrant ssh
```

This will open a new terminal window with a shell prompt inside the virtual machine.

We have arranged that you log in as root, there is another user on the system that we will use sometimes in the demo (vagrant).


That's it! You have successfully executed your first Vagrant and launched a virtual machine.

## using tmux.

Sometimes will be useful to have a split panel, and for that intent we will use tmux, a quick intro to tmux is:

To start Tmux, on the terminal window type the following command:

```
[~/] tmux
```

This will change the look of the terminal, you can split the screen with `CTL-b`  (that's ctrl and the letter b at the same time) and `%` (the percentage symbol, usually that's shift+5) for vertical and “ (quotes) horizontal.

You can click each panel to make it focus, and you can scroll up and down using your wheel on the mouse.

## shutdown and recreating the virtual machine

Virtual machines on laptops are useful for development, testing, or any other ephemeral and isolated purposes you need. when you are done, you can just discard them.

To shut down the virtual machine, run the `vagrant halt` command, and to delete it entirely, use the `vagrant destroy` command.

## configuring your env

If you want to configure your env, like setting the editor (we are going to be editing files, unles you are fine with nano, you might want to change your editor), create a file in conf/bashrc.local.conf and then reprovision (or destroy and recreate) the virtual machine, example



```bash
# .bash_profile
# conf/bashrc.local.conf

export EDITOR=$(which vim)

# User specific environment and startup programs
```


```
[~/workshop ] vagrant provision
```

## Environment Prerequisites

Some of the features we will be demo-ing do not work well when SELinux is set to enforcing mode. The virtual machine we will be using already sets SELinux to permissive mode. You can verify this in the virtual machine by running:

```
[~]# getenforce
```

If `getenforce` says you are in enforcing mode, you can set it to permissive by running:

```
[~]# setenforce Permissive
```

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)
