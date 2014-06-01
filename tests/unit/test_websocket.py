import asyncio
import json
import pytest
from conftest import setup_asyncio as setup_function
from conftest import teardown_asyncio as teardown_function


def test_websocket():
    from geoffrey.websocket import WebsocketServer
    assert WebsocketServer(consumers=[])


def test_handshake_unknown_consumer(wsserver, websocket, loop):
    from geoffrey.websocket import HandshakeError

    raw = json.dumps({'consumer_id': 'notfound'})
    wsconn = websocket([raw])()
    hs = wsserver.handshake(wsconn)
    with pytest.raises(HandshakeError):
        loop.run_until_complete(hs)


def test_handshake_bad_payload(wsserver, websocket, loop):
    from geoffrey.websocket import HandshakeError

    raw = json.dumps("baaaddataaa")
    wsconn = websocket([raw])()
    hs = wsserver.handshake(wsconn)
    with pytest.raises(HandshakeError):
        loop.run_until_complete(hs)


def test_handshake_empty_consumer_id(wsserver, websocket, loop):
    from geoffrey.websocket import HandshakeError

    raw = json.dumps({'badkey': 'badvalue'})
    wsconn = websocket([raw])()
    hs = wsserver.handshake(wsconn)
    with pytest.raises(HandshakeError):
        loop.run_until_complete(hs)


def test_handshake_ok(wsserver, websocket, loop):
    from geoffrey.subscription import Consumer
    raw = json.dumps({'consumer_id': 'consumer'})
    wsconn = websocket([raw])()
    hs = wsserver.handshake(wsconn)
    res = loop.run_until_complete(hs)
    assert isinstance(res, Consumer)


def test_communicate(wsserver, websocket_ready, loop, consumer, event):
    consumer.criteria = [{}]
    comm = wsserver.communicate(websocket_ready, consumer)
    @asyncio.coroutine
    def put_and_wait():
        yield from consumer.put(event)
        while websocket_ready._send.qsize() == 0:
            yield from asyncio.sleep(1)

    tasks = asyncio.wait([comm, put_and_wait()],
                         return_when=asyncio.FIRST_COMPLETED)
    loop.run_until_complete(tasks)

    assert websocket_ready._send.qsize() == 1


def test_server(wsserver, websocket_ready, loop, event):
    srv = wsserver.server(websocket_ready)
    consumer = wsserver.consumers['consumer']

    @asyncio.coroutine
    def put_and_wait():
        yield from consumer.put(event)
        while websocket_ready._send.qsize() == 0:
            yield from asyncio.sleep(1)

    tasks = asyncio.wait([srv, put_and_wait()],
                         return_when=asyncio.FIRST_COMPLETED)
    loop.run_until_complete(tasks)

    assert websocket_ready._send.qsize() == 1
