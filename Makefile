.PHONY: clean develop test wip coverage
clean:
	python setup.py clean
	find . -name '*.pyc' -type f | xargs rm -f
	find . -name __pycache__ -type d | xargs rm -Rf
	rm -Rf htmlcov
	coverage erase
develop:
	pip install -q -r requirements/develop.txt
	pip install -q -e .
unit-test: clean 
	coverage run `which py.test` -m "not wip" tests/unit
unit-wip: clean
	coverage run `which py.test` -m wip --capture=no --pdb tests/unit
behaviour-test: clean
	coverage run `which behave` --tags ~@wip tests/behave/features
behaviour-wip: clean
	coverage run `which behave` --tags @wip --no-capture tests/behave/features
cov-report:
	coverage combine
	coverage html
test-all: clean
	pip install -q -r requirements/tests.txt
	tox
	coverage combine
	coverage html
vagrant-test:
	vagrant up
	vagrant ssh -- "/bin/bash -c 'source /home/vagrant/bin/activate && cd /vagrant && make test-all'"
