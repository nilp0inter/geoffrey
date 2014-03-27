vagrant up
vagrant ssh -c '\
    sudo rsync -r --exclude=.tox --exclude=.git --exclude=.vagrant /vagrant/ /tmp/geoffrey && \
    cd /tmp/geoffrey && \
    sudo sh ./runtests.sh && \
    cp -Rvf htmlcov /vagrant/'

if [ $? -eq 0 ]
then
    echo "Congratulations! All tests passed. You should have an html coverage report at ./htmlcov/ ."
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi
