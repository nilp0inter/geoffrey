#!/bin/bash

# If deps are installed exit gracefully.
which python3.3 && which python3.4 && exit 0

apt-get update

# Add deadsnakes ppa https://launchpad.net/~fkrull/+archive/deadsnakes
apt-get install -y python-software-properties python-pip
add-apt-repository -y ppa:fkrull/deadsnakes
apt-get update

#
# Python 3.3
#
apt-get install -y python3.3 python3.3-dev

#
# Python 3.4
#
apt-get install -y python3.4 python3.4-dev

pip install virtualenv
su vagrant -c "virtualenv -p /usr/bin/python3.4 /home/vagrant"
su vagrant -c "/home/vagrant/bin/pip install -e /vagrant"

echo "source ~/bin/activate" >> /home/vagrant/.bashrc
echo "export GEOFFREYDEBUG=1" >> /home/vagrant/.bashrc

source /home/vagrant/bin/activate
cd /vagrant
pip install -r requirements/tests.txt
make develop

# Setup examples & configuration
apt-get install -y git-core
su - vagrant -c "git clone https://github.com/GeoffreyCI/fakeproject1.git /home/vagrant/fakeproject1"
su - vagrant -c "git clone https://github.com/GeoffreyCI/fakeproject2.git /home/vagrant/fakeproject2"
cp -Rvf /vagrant/examples/vagrantconfig /home/vagrant/.geoffrey
chown -R vagrant:vagrant /home/vagrant/.geoffrey

#
# Install development plugins
#
## geoffrey-pytest
su - vagrant -c "git clone https://github.com/GeoffreyCI/geoffrey-pytest /home/vagrant/geoffrey-pytest"
su - vagrant -c "/home/vagrant/bin/pip install -e /home/vagrant/geoffrey-pytest"

## geoffrey-todo
su - vagrant -c "git clone https://github.com/GeoffreyCI/geoffrey-todo /home/vagrant/geoffrey-todo"
su - vagrant -c "/home/vagrant/bin/pip install -e /home/vagrant/geoffrey-todo"
