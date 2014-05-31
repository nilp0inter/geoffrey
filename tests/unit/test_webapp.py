import os
import json
from tempfile import TemporaryDirectory

from webtest import TestApp
from bottle import Bottle
from geoffrey.server import Server
from geoffrey import utils


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
    consumer_created = app.post('/api/v1/consumer', {}).body.decode('utf-8')
    consumer_data = json.loads(consumer_created)
    consumer = app.delete('/api/v1/consumer/{}'.format(consumer_data['id']))
    assert consumer.status_code == 200


def test_get_projects():
    """ Test get current projects with web interface """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = Server(config=config_file)
        project1 = 'newproject'
        project2 = 'ìòúü?!¿ñ¡'
        server.create_project(project1)
        server.create_project(project2)
        app = TestApp(server.get_webapp(bottle=Bottle))
        projects = app.get('/api/v1/projects')
        project_data = json.loads(projects.body.decode('utf-8'))
        assert projects.status_code == 200
        assert len(project_data) == 2
        assert {'id': utils.slugify(project2),
                'name': project2} in project_data


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
