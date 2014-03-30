pip install -r requirements/tests.txt
coverage erase
rm -Rf htmlcov
tox
coverage combine
coverage html
