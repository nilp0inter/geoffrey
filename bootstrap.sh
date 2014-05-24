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
