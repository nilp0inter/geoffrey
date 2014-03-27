import os
import asyncio
from geoffrey.deps.aiobottle import AsyncBottle, AsyncServer
from bottle import static_file, TEMPLATE_PATH, jinja2_view


BASE = os.path.join(os.path.dirname(__file__), "web")
TEMPLATE_PATH[:] = [BASE]
app = AsyncBottle()


def run(host='0.0.0.0', port=8700, websocket_port=8701):
    from bottle import run

    @app.get('/')
    @jinja2_view('index.html')
    def index():
        return {'host': host, 'port': websocket_port, 'path': 'test'}

    @app.get('/assets/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root=os.path.join(BASE, 'assets'))

    run(app, host=host, port=port, server=AsyncServer, quiet=True)

if __name__ == '__main__':
    run()
