from geoffrey import plugin
from geoffrey.plugins.dummy import DummyPlugin
import configparser


def test_plugin_load():
    config = configparser.ConfigParser()
    config.add_section('plugin:DummyPlugin')
    plugin_list = plugin.get_plugins(config)
    assert any([isinstance(p, DummyPlugin) for p in plugin_list])
