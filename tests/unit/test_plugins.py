from geoffrey import plugin
from geoffrey.plugins.dummy import DummyPlugin

def test_plugin_load():
    config = None
    plugin_list = plugin.get_plugins(config)
    assert any([isinstance(p, DummyPlugin) for p in plugin_list])
