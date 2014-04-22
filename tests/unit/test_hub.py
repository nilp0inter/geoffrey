

def test_hub(hub):
    assert hub


def test_send_event(hub, event):
    hub.send(event)
    assert event in hub.events
