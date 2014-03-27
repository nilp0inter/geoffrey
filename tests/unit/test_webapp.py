# from webtest import TestApp
# from bottle import Bottle
# from geoffrey.server import Server
#
#
# def test_index():
#     server = Server()
#     app = TestApp(server.get_webapp(bottle=Bottle))
#     index = app.get('/')
#     assert index.status_code == 200
#     assert b'<title>Geoffrey' in index.body
