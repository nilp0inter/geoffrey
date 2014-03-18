# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "Puppetlabs Ubuntu 12.04.2 x86_64, VBox 4.2.10"

  # From: http://www.vagrantbox.es/
  config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-server-12042-x64-vbox4210.box"

  config.vm.network :forwarded_port, guest: 8700, host: 8700
  config.vm.network :forwarded_port, guest: 8701, host: 8701

  config.vm.provision :shell, :path => "bootstrap.sh"

end
