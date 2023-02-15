# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|
  config.vm.box = "aleivag/fedora37"
  config.vm.box_check_update = false

  config.vm.synced_folder "workshop", "/opt/workshop"
  config.vm.synced_folder "bin", "/opt/bin"

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "1024"
  end

 config.vm.provision "shell", path: "bin/provision-vagrant"
end
