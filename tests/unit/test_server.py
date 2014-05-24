def test_server():
    from geoffrey.server import Server
    assert Server()


def test_server_has_hub():
    from geoffrey.server import Server
    from geoffrey.hub import EventHUB
    assert isinstance(Server().hub, EventHUB)

