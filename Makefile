.PHONY: develop test
clean:
	python setup.py clean
	find . -name '*.pyc' -type f | xargs rm -f
	find . -name __pycache__ -type d | xargs rm -Rf
develop:
	pip install -q -r requirements/develop.txt
	pip install -q -e .
test: develop clean 
	py.test --cov geoffrey -m "not wip" --capture=no tests/unit
wip: develop clean
	py.test -m wip --capture=no tests/unit
