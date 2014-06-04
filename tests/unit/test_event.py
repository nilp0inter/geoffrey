import json


def test_event(event):
    assert event


def test_event_default_json(event):
    data = json.loads(event.dumps())

    assert data['project'] is None
    assert data['plugin'] is None
    assert data['key'] is None
    assert data['value'] == {}


def test_event_with_values_json():
    from geoffrey import data
    event = data.Event(project='myproject',
                        plugin='myplugin',
                        key='mykey',
                        value='myvalue')

    data = json.loads(event.dumps())

    assert data['project'] == 'myproject'
    assert data['plugin'] == 'myplugin'
    assert data['key'] == 'mykey'
    assert data['value'] == {'value': 'myvalue'}
