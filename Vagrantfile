# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|
  config.vm.box = "aleivag/fedora37"
  config.vm.box_version = "2023.03.08"
  config.vm.box_check_update = false

  config.vm.synced_folder "workshop", "/opt/workshop"
  config.vm.synced_folder "bin", "/opt/bin"
  config.vm.synced_folder ".", "/root/.local"
  config.vm.synced_folder "conf", "/opt/conf"
  config.vm.synced_folder ".", "/usr/local/src/workshop"


  config.vm.provider "virtualbox" do |vb|
     vb.memory = "1024"
  end

  config.vm.provision "shell", inline: "python3 /usr/local/src/workshop/bin/provision-host"
end