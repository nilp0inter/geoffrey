from tempfile import TemporaryDirectory
import os

import pytest

import geoffrey


@pytest.mark.wip
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
        assert 'newproject' in server.projects


@pytest.mark.wip
def test_delete_project():
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        project_dir = os.path.join(configdir, 'projects', 'removemeproject')
        project_config = os.path.join(project_dir, 'removemeproject.conf')
        os.makedirs(project_dir)
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')

        server = geoffrey.Server(config=config_file)

        server.delete_project('removemeproject')

        assert not os.path.exists(project_config)
        assert not os.path.exists(project_dir)


@pytest.mark.wip
def test_delete_unmanaged_project():
    """The server can't delete unamanged projects."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        server = geoffrey.Server(config=config_file)

        project_dir = os.path.join(configdir, 'projects', 'removemeproject')
        project_config = os.path.join(project_dir, 'removemeproject.conf')
        os.makedirs(project_dir)
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')

        with pytest.raises(RuntimeError):
            server.delete_project('removemeproject')

        assert os.path.exists(project_config)
        assert os.path.exists(project_dir)
