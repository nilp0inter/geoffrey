#!/bin/bash

apt-get update

apt-get install -y python-software-properties
add-apt-repository -y ppa:fkrull/deadsnakes

apt-get update
apt-get install -y python3.4 python3.4-dev

python3.4m -m ensurepip
cd /vagrant
python3.4 setup.py develop

apt-get install -y graphviz
pip3.4 install pylint radon flake8

cp /vagrant/config/example.conf /home/vagrant/.geoffreyrc
