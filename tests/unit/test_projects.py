from tempfile import TemporaryDirectory
import os

import geoffrey


def test_create_project():
    """Create a new project."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)
        server.create_project('newproject')
        assert os.path.exists(os.path.join(configdir, 'projects',
                                           'newproject'))
        assert os.path.exists(os.path.join(configdir, 'projects', 'newproject',
                                           'newproject.conf'))
