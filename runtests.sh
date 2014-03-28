pip install -r requirements/tests.txt
coverage erase
tox
coverage combine
coverage html
