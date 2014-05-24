from cgi import escape
from webtest import TestApp
from bottle import Bottle
from geoffrey.server import Server


def test_index():
    """ Test webserver index page """

    server = Server()
    app = TestApp(server.get_webapp(bottle=Bottle))
    index = app.get('/')
    assert index.status_code == 200
    assert b'<title>Geoffrey' in index.body


def test_add_consumer():
    """ Test add consumer for web interface """

    server = Server()
    app = TestApp(server.get_webapp(bottle=Bottle))
    consumer = app.post('/api/v1/consumer', {})
    assert consumer.status_code == 200
    assert b'"id":' in consumer.body
    assert b'"ws":' in consumer.body


def test_remove_consumer():
    """ Test remove consumer for web interface """

    server = Server()
    app = TestApp(server.get_webapp(bottle=Bottle))
    consumer = app.delete('/api/v1/consumer')
    assert consumer.status_code == 200


def test_get_projects():
    """ Test get current projects with web interface """

    server = Server()
    app = TestApp(server.get_webapp(bottle=Bottle))
    projects = app.get('/api/v1/projects')
    assert projects.status_code == 200

def test_get_api():
    """ Test current API definition """

    server = Server()
    app = TestApp(server.get_webapp(bottle=Bottle))
    api = app.get('/api/v1')
    assert api.status_code == 200
    assert b"/api/v1" in api.body
    assert b"/api/v1/&lt;project_id&gt;/&lt;plugin_id&gt;/source" in api.body
    assert b"/api/v1/&lt;project_id&gt;/&lt;plugin_id&gt;/state" in api.body
    assert b"/api/v1/&lt;project_id&gt;/plugins" in api.body
    assert b"/api/v1/consumer" in api.body
    assert b"/api/v1/projects" in api.body
    assert b"/api/v1/subscription/&lt;consumer_id&gt;" in api.body

