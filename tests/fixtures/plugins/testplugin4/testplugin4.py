from geoffrey.plugin import GeoffreyPlugin

class TestPlugin4(GeoffreyPlugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_app()

    def configure_app(self):
        self.app.route('/dummymethod', callback=self.dummymethod)

    def dummymethod(self, *args, **kwargs):
        return "OK"
