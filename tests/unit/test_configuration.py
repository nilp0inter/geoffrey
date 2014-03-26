from tempfile import TemporaryDirectory
import os

import pytest

import geoffrey


def test_autocreate_conf():
    """Autocreate main configuration if missing."""

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'doesnotexists', 'geoffrey.conf')
        geoffrey.Server.read_main_config(config_file)
        assert os.path.isfile(config_file)


def test_autocreate_project_dir():
    """Autocreate projects root if missing."""

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        geoffrey.Server(config=config_file)
        assert os.path.isdir(os.path.join(configdir, 'projects'))


def test_server_projects():
    """The server knows its active projects."""

    fake_projects = ['project1', 'project2']

    with TemporaryDirectory() as configdir:

        # Create the fake config structure
        config_file = os.path.join(configdir, 'geoffrey.conf')
        with open(config_file, 'w') as f:
            f.write('[geoffrey]\n\n')
        for project in fake_projects:
            fake_project_dir = os.path.join(configdir, 'projects', project)
            os.makedirs(fake_project_dir)
            with open(os.path.join(fake_project_dir,
                                   '{}.conf'.format(project)), 'w') as f:
                f.write('[project]\n\n')

        # Create the server, read the config and test project existence
        server = geoffrey.Server(config=config_file)
        for project in fake_projects:
            assert project in server.projects


def test_main_config_must_be_file():
    """TypeError if main config is not a file."""

    with TemporaryDirectory() as configdir:
        with pytest.raises(TypeError):
            geoffrey.Server.read_main_config(configdir)


def test_project_configuration():
    """A project can read its own configuration."""
    with TemporaryDirectory() as projectdir:
        project_config = os.path.join(projectdir, 'projectname.conf')
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')
        project = geoffrey.Project(name='projectname', config=project_config)
        assert 'project' in project.config.sections()
