# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "Puppetlabs Ubuntu 12.04.2 x86_64, VBox 4.2.10"

  # From: http://www.vagrantbox.es/
  config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-server-12042-x64-vbox4210.box"

  config.vm.provision :shell, :path => "bootstrap.sh"

end


# # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
# VAGRANTFILE_API_VERSION = "2"
#
# Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
#   # All Vagrant configuration is done here. The most common configuration
#   # options are documented and commented below. For a complete reference,
#   # please see the online documentation at vagrantup.com.
#
#   # Every Vagrant virtual environment requires a box to build off of.
#   config.vm.box = "windows7"
#   config.vm.guest = :windows
#   config.vm.network :forwarded_port, guest: 5985, host: 5985, id: "winrm", auto_correct: true
#
#   config.vm.provider :virtualbox do |vb|
#     # Don't boot with headless mode
#     # vb.gui = true
#
#     # Use VBoxManage to customize the VM. For example to change memory:
#     vb.customize ["modifyvm", :id, "--memory", "1024"]
#   end
#
#   config.vm.provision :shell, :path => "test.bat"
# end
