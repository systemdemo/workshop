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

and start your machine with

```bash
[~/workshop ] vagrant up
```

This will take care of downloading a base image and starting a virtual box machine with it, feel free take a sneak peak at the [Vagrantfile](https://github.com/systemdemo/workshop/blob/main/Vagrantfile) to understand what exactly you are doing.


