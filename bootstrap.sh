#!/bin/bash

# If deps are installed exit gracefully.
which python3.3 && which python3.4 && exit 0

apt-get update

# Add deadsnakes ppa https://launchpad.net/~fkrull/+archive/deadsnakes
apt-get install -y python-software-properties
add-apt-repository -y ppa:fkrull/deadsnakes
apt-get update

#
# Python 3.3
#
apt-get install -y python3.3 python3.3-dev

# Python 3.3 (pip) https://gist.github.com/kura/8517802
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O /tmp/ez_setup.py
python3.3 /tmp/ez_setup.py
easy_install-3.3 pip

#
# Python 3.4
#
apt-get install -y python3.4 python3.4-dev

# Python 3.4 (pip)
python3.4 -m ensurepip

# We need virtualenv for tox testing
pip3.3 install virtualenv

pip3.4 install -e /vagrant/
