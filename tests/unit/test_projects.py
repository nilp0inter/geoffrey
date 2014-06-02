from tempfile import TemporaryDirectory
import os

import pytest

from geoffrey.server import Server


def test_create_project():
    """Create a new project."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = Server(config=config_file)
        server.create_project('newproject')

        project_dir = os.path.join(configdir, 'projects', 'newproject')

        assert os.path.exists(project_dir)
        assert os.path.exists(os.path.join(project_dir, 'project.conf'))
        assert 'newproject' in server.projects


def test_delete_project():
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project_dir = os.path.join(configdir, 'projects', 'removemeproject')
        project_config = os.path.join(project_dir, 'project.conf')
        os.makedirs(project_dir)
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')

        server = Server(config=config_file)

        server.delete_project('removemeproject')

        assert not os.path.exists(project_config)
        assert not os.path.exists(project_dir)


def test_delete_unmanaged_project():
    """The server can't delete unamanged projects."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = Server(config=config_file)

        project_dir = os.path.join(configdir, 'projects', 'removemeproject')
        project_config = os.path.join(project_dir, 'project.conf')
        os.makedirs(project_dir)
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')

        with pytest.raises(RuntimeError):
            server.delete_project('removemeproject')

        assert os.path.exists(project_config)
        assert os.path.exists(project_dir)
