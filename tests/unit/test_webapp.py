import os
import json
from tempfile import TemporaryDirectory

import pytest
from webtest import TestApp as _TestApp
from bottle import Bottle
from geoffrey.server import Server
from geoffrey.webserver import WebServer
from geoffrey import utils


def test_index():
    """ Test webserver index page """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    index = app.get('/')
    assert index.status_code == 200
    assert b'<title>Geoffrey' in index.body


def test_add_consumer():
    """ Test add consumer for web interface """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    consumer = app.post('/api/v1/consumer', {})
    assert consumer.status_code == 200
    assert b'"id":' in consumer.body
    assert b'"ws":' in consumer.body
    assert ((b'"ws://127.0.0.1:8701"' in consumer.body) or
            (b'"ws://localhost:8701"' in consumer.body))


def test_remove_consumer():
    """ Test remove consumer for web interface """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    consumer_created = app.post('/api/v1/consumer', {}).body.decode('utf-8')
    consumer_data = json.loads(consumer_created)
    consumer = app.delete('/api/v1/consumer/{}'.format(consumer_data['id']))
    assert consumer.status_code == 200


def test_remove_nonexistant_consumer():
    """ Test remove a non existant consumer for web interface """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    consumer_id = 'NONEXISTINGCONSUMER'
    consumer = app.delete('/api/v1/consumer/{}'.format(consumer_id),
                          expect_errors=404)
    assert consumer.status_code == 404


def test_get_projects():
    """ Test get current projects with web interface """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = Server(config=config_file)
        project1 = 'newproject'
        project2 = 'ìòúü?!¿ñ¡'
        server.create_project(project1)
        server.create_project(project2)
        app = _TestApp(WebServer(server=server).app)
        projects = app.get('/api/v1/projects')
        project_data = json.loads(projects.body.decode('utf-8'))
        assert projects.status_code == 200
        assert len(project_data) == 2
        assert {'id': utils.slugify(project2),
                'name': project2} in project_data


def test_get_plugins():
    """ Test get plugin list for project """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'dummyplugin'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, 'project.conf')
        os.makedirs(project_path)
        content = """[project]

        [plugin:{plugin_name}]
        """.format(plugin_name=plugin_name, project_path=project_path)

        utils.write_template(config, content)
        server = Server(config=config_file)
        app = _TestApp(WebServer(server=server).app)
        plugins = app.get('/api/v1/{}/plugins'.format(project))
        assert plugins.status_code == 200
        assert plugins.json == [{'id': 'dummyplugin'}]


def test_plugin_no_datafiles(testplugin1):
    """ Test get plugin source. No exists """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'testplugin1'
        plugin_language = 'js'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, 'project.conf')
        os.makedirs(project_path)
        content = """[project]

        [plugin:{plugin_name}]

        paths={project_path}
        """.format(plugin_name=plugin_name, project_path=project_path)

        utils.write_template(config, content)
        server = Server(config=config_file)
        server.projects[project].plugins[plugin_name] = testplugin1(config=config)

        app = _TestApp(WebServer(server=server).app)
        plugin_s = app.get('/api/v1/{project_name}/'
                           '{plugin_name}/source/'
                           '{language}'.format(project_name=project,
                                               plugin_name=plugin_name,
                                               language=plugin_language),
                           expect_errors=True)
        assert plugin_s.status_code == 404

def test_plugin_source(testplugin2):
    """ Test get plugin source. File exists. """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'testplugin2'
        plugin_language = 'js'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, 'project.conf')
        os.makedirs(project_path)
        content = """[project]

        [plugin:{plugin_name}]

        paths={project_path}
        """.format(plugin_name=plugin_name, project_path=project_path)

        utils.write_template(config, content)
        server = Server(config=config_file)
        server.projects[project].plugins[plugin_name] = testplugin2(config=None)

        ws = WebServer(server=server)
        app = _TestApp(ws.app)
        plugin_s = app.get('/api/v1/{project_name}/'
                           '{plugin_name}/source/'
                           '{language}'.format(project_name=project,
                                               plugin_name=plugin_name,
                                               language=plugin_language))
        assert plugin_s.status_code == 200
        assert plugin_s.body == b'javascript'


def test_plugin_source_invalid_language(testplugin2):
    """ Test get plugin source. Language does no exists """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'testplugin2'
        plugin_language = 'py'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, 'project.conf')
        os.makedirs(project_path)
        content = """[project]

        [plugin:{plugin_name}]

        paths={project_path}
        """.format(plugin_name=plugin_name, project_path=project_path)

        utils.write_template(config, content)
        server = Server(config=config_file)
        server.projects[project].plugins[plugin_name] = testplugin2(config=None)

        app = _TestApp(WebServer(server=server).app)
        plugin_s = app.get('/api/v1/{project_name}/'
                           '{plugin_name}/source/'
                           '{language}'.format(project_name=project,
                                               plugin_name=plugin_name,
                                               language=plugin_language),
                           expect_errors=True)

        assert plugin_s.status_code == 404


def test_plugin_state():
    """ Test get plugin state """
    from geoffrey.data import State

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'FakePlugin'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, '{}.conf'.format(project))
        os.makedirs(project_path)

        content = """[project]
        """.format(plugin_name=plugin_name)

        utils.write_template(config, content)
        server = Server(config=config_file)

        state1 = State(project=project, plugin=plugin_name, key='goodkey', value='something')
        server.hub.states[state1._key] = state1._value
        state2 = State(project='badproject', plugin=plugin_name, key='goodkey', value='something')
        server.hub.states[state2._key] = state2._value

        app = _TestApp(WebServer(server=server).app)
        plugin_s = app.get('/api/v1/{project_name}/'
                           '{plugin}/state'.format(project_name=project,
                                                   plugin=plugin_name))
        states = json.loads(plugin_s.body.decode('utf-8'))

        assert plugin_s.status_code == 200
        assert len(states) == 1
        assert states[0]['project'] == state1.project
        assert states[0]['plugin'] == state1.plugin
        assert states[0]['key'] == state1.key
        assert states[0]['value'] == state1._value


def test_server_static():
    """ Test get static file """
    server = Server()
    app = _TestApp(WebServer(server=server).app)
    static_file = 'geoffrey.jpg'
    static = app.get('/assets/{}'.format(static_file))
    assert static.status_code == 200


def test_get_api():
    """ Test current API definition """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    api = app.get('/api/v1')
    assert api.status_code == 200
    assert b"/api/v1" in api.body
    assert b"/api/v1/&lt;project_id&gt;/&lt;plugin_id&gt;/source" in api.body
    assert b"/api/v1/&lt;project_id&gt;/&lt;plugin_id&gt;/state" in api.body
    assert b"/api/v1/&lt;project_id&gt;/plugins" in api.body
    assert b"/api/v1/consumer" in api.body
    assert b"/api/v1/projects" in api.body
    assert b"/api/v1/subscription/&lt;consumer_id&gt;" in api.body


def test_subscription_noconsumer():
    """ Test modify subscription of a non existant consumer. """

    server = Server()
    app = _TestApp(WebServer(server=server).app)
    consumer_id = 'NONEXISTINGCONSUMER'
    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {'criteria': [{}]}, expect_errors=404)
    assert res.status_code == 404


def test_subscription_badrequest(consumer):
    """ Test sending a bad payload in subscription request. """

    server = Server()
    consumer_id = 'goodconsumer'
    server.consumers[consumer_id] = consumer

    app = _TestApp(WebServer(server=server).app)

    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {'nocriteria': [{}]}, expect_errors=400)
    assert res.status_code == 400

    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {'criteria': "badcriteria"}, expect_errors=400)
    assert res.status_code == 400

    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {'criteria': [3]}, expect_errors=400)
    assert res.status_code == 400

    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {'criteria': [{"abc": 3}]}, expect_errors=400)
    assert res.status_code == 400


def test_subscription_goodrequest(consumer):
    """ Test change successfully a consumer subscription. """

    server = Server()
    consumer_id = 'goodconsumer'
    server.consumers[consumer_id] = consumer
    criteria = [{"plugin": "goodplugin"}]

    assert consumer.criteria != criteria

    app = _TestApp(WebServer(server=server).app)
    res = app.post_json('/api/v1/subscription/{}'.format(consumer_id),
                        {"criteria": criteria})

    assert res.status_code == 200
    assert consumer.criteria == criteria


def test_plugin_api_injection(testplugin4):
    """ Test get plugin source. No exists """

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project = 'newproject'
        plugin_name = 'testplugin4'
        project_path = os.path.join(configdir, 'projects', project)
        config = os.path.join(project_path, 'project.conf')
        os.makedirs(project_path)
        content = """[project]

        [plugin:{plugin_name}]
        """.format(plugin_name=plugin_name, project_path=project_path)

        utils.write_template(config, content)
        server = Server(config=config_file)
        plugin = testplugin4(config=config)
        server.projects[project].plugins[plugin_name] = plugin
        plugin.start()

        app = _TestApp(WebServer(server=server).app)
        plugin_m = app.get('/api/v1/{project_name}/'
                           '{plugin_name}/method/'
                           'dummymethod'.format(project_name=project,
                                                plugin_name=plugin_name))

        assert plugin_m.status_code == 200

