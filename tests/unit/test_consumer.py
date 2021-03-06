import pytest


def test_consumer():
    from geoffrey.subscription import Consumer
    assert Consumer()


def test_consumer_no_criteria(consumer, event):
    consumer.put_nowait(event)
    assert consumer.qsize() == 0


def test_consumer_match_all(consumer, event):
    consumer.criteria = [{}]
    consumer.put_nowait(event)
    assert consumer.qsize() == 1


def test_consumer_match_type(consumer):
    from geoffrey import data

    consumer.criteria = [{'type': 'modified'}]

    event1 = data.Event(type=data.EventType.modified)
    consumer.put_nowait(event1)

    event2 = data.Event(type=data.EventType.custom)
    consumer.put_nowait(event2)

    assert consumer.qsize() == 1
    assert consumer.get_nowait() == event1


def test_consumer_match_project(consumer):
    from geoffrey import data

    consumer.criteria = [{'project': 'goodproject'}]

    event1 = data.Event(plugin=None, project="goodproject", key=None)
    consumer.put_nowait(event1)

    event2 = data.Event(plugin=None, project="badproject", key=None)
    consumer.put_nowait(event2)

    assert consumer.qsize() == 1
    assert consumer.get_nowait() == event1


def test_consumer_match_plugin(consumer):
    from geoffrey import data

    consumer.criteria = [{'plugin': 'goodplugin'}]

    event1 = data.Event(plugin="goodplugin", project=None, key=None)
    consumer.put_nowait(event1)

    event2 = data.Event(plugin="badplugin", project=None, key=None)
    consumer.put_nowait(event2)

    assert consumer.qsize() == 1
    assert consumer.get_nowait() == event1


def test_consumer_match_key(consumer):
    from geoffrey import data

    consumer.criteria = [{'key': 'goodkey'}]

    event1 = data.Event(plugin=None, project=None, key="goodkey")
    consumer.put_nowait(event1)

    event2 = data.Event(plugin=None, project=None, key="badkey")
    consumer.put_nowait(event2)

    assert consumer.qsize() == 1
    assert consumer.get_nowait() == event1


def test_consumer_composed_criteria(consumer):
    from geoffrey import data

    consumer.criteria = [{'project': 'goodproject', 'key': 'goodkey'}]

    event1 = data.Event(plugin=None, project="goodproject", key="goodkey")
    consumer.put_nowait(event1)

    event2 = data.Event(plugin=None, project="goodproject", key="badkey")
    consumer.put_nowait(event2)

    event3 = data.Event(plugin=None, project="badproject", key="goodkey")
    consumer.put_nowait(event3)

    assert consumer.qsize() == 1
    assert consumer.get_nowait() == event1


def test_consumer_multiple_criteria(consumer):
    from geoffrey import data

    consumer.criteria = [{'plugin': 'goodplugin'},
                         {'project': 'goodproject'}]

    event1 = data.Event(plugin="goodplugin", project="goodproject", key=None)
    consumer.put_nowait(event1)

    event2 = data.Event(plugin="badplugin", project="goodproject", key=None)
    consumer.put_nowait(event2)

    event3 = data.Event(plugin="goodplugin", project="badproject", key=None)
    consumer.put_nowait(event3)

    event4 = data.Event(plugin="badplugin", project="badproject", key=None)
    consumer.put_nowait(event4)

    assert consumer.qsize() == 3
    assert consumer.get_nowait() == event1
    assert consumer.get_nowait() == event2
    assert consumer.get_nowait() == event3
