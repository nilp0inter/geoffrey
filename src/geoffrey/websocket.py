#pylint: disable=I0011,E1101
import asyncio
import logging
import json

from websockets.exceptions import InvalidState

logger = logging.getLogger(__name__)


class HandshakeError(Exception):
    pass


class WebsocketServer:
    def __init__(self, consumers):
        self.consumers = consumers

    @asyncio.coroutine
    def handshake(self, websocket):
        """Do the handshake with the websocket. Return the consumer."""
        rawpayload = yield from websocket.recv()
        try:
            payload = json.loads(rawpayload)
            consumer_id = payload.get('consumer_id', None)
        except:
            raise HandshakeError("Wrong payload")
        else:
            if consumer_id is None:
                raise HandshakeError(
                    "`consumer_id` not provided in %s" % websocket)
        if consumer_id not in self.consumers:
            raise HandshakeError("Consumer %s is not registered" % consumer_id)
        return self.consumers[consumer_id]

    @asyncio.coroutine
    def communicate(self, websocket, consumer):
        while True:
            event = yield from consumer.get()
            rawevent = event.dumps()
            try:
                yield from websocket.send(rawevent)
            except InvalidState:
                return
            except:  # pragma: no cover
                logger.exception("Websocket error sending data: %s",
                                 rawevent)

    @asyncio.coroutine
    def server(self, websocket, *args):
        try:
            consumer = yield from self.handshake(websocket)
        except HandshakeError:  # pragma: no cover
            logger.exception("Websocket communication error in handshake")
        else:
            yield from self.communicate(websocket, consumer)
        logger.info("Websocket closed.")
