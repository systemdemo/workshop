# dynamic users
    - use `ps` to show that the running user is not root

# mount ns - the basics
    - use nsenter to go into the namespace

# RootDirectory/RootImage - TODO ask Alvaro to install it somewhere
    - show how chroot works.
    - then show how it works with the systemd unit
    - run a cute debian program. compare it to host

# PrivateNetwork
    - isolate all network. use this to seg way into IPAddressDeny/Allow

# IPAddressAllow/Deny
    - use `systemd-run bash` because it's too hard to demo sockets filtering otherwise
