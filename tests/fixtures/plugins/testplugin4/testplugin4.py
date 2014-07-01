from geoffrey.plugin import GeoffreyPlugin

class TestPlugin4(GeoffreyPlugin):

    def configure_app(self):
        self.app.route('/dummymethod', callback=self.dummymethod)
        super().configure_app()

    def dummymethod(self, *args, **kwargs):
        return "OK"
