from tempfile import TemporaryDirectory
import os

import pytest

from geoffrey.server import Server
from geoffrey.project import Project

def test_autocreate_conf():
    """Autocreate main configuration if missing."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'doesnotexists', 'geoffrey.conf')
        Server.read_main_config(config_file)
        assert os.path.isfile(config_file)


def test_autocreate_project_dir():
    """Autocreate projects root if missing."""
    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        Server(config=config_file)
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
            with open(os.path.join(fake_project_dir, 'project.conf'), 'w') as f:
                f.write('[project]\n\n')

        # Weird cases:
        # 1. Project config is a dir instead of a file
        os.makedirs(os.path.join(configdir, 'projects',
                                 'project3', 'project.conf'))

        # 2. Files inside `projects` dir.
        with open(os.path.join(configdir, 'projects', 'project4'), 'w') as f:
            f.write('nothing')

        # Create the server, read the config and test project existence
        server = Server(config=config_file)
        for project in fake_projects:
            assert project in server.projects
            assert isinstance(server.projects[project],
                              Project)

        # Weird cases
        assert 'project3' not in server.projects
        assert 'project4' not in server.projects


def test_main_config_must_be_file():
    """TypeError if main config is not a file."""

    with TemporaryDirectory() as configdir:
        with pytest.raises(TypeError):
            Server.read_main_config(configdir)


def test_project_configuration():
    """A project can read its own configuration."""
    with TemporaryDirectory() as projectdir:
        project_config = os.path.join(projectdir, 'project.conf')
        with open(project_config, 'w') as f:
            f.write('[project]\n\n')
        project = Project(name='projectname',
                                           config=project_config)
        assert 'project' in project.config.sections()

def test_project_plugins():
    """The project know its active plugins."""
    from geoffrey.plugins.dummy import DummyPlugin1, DummyPlugin2

    with TemporaryDirectory() as configdir:
        config_file = os.path.join(configdir, 'geoffrey.conf')
        fake_project_dir = os.path.join(configdir, 'projects', 'project1')
        os.makedirs(fake_project_dir)
        fake_project_config = os.path.join(fake_project_dir, 'project.conf')
        with open(fake_project_config, 'w') as f:
            f.write("""
                [project]
                [plugin:dummyplugin1]
                [plugin:dummyplugin2]""")

        server = Server(config=config_file)
        plugins = server.projects['project1'].plugins
        assert 'dummyplugin1' in plugins
        assert isinstance(plugins['dummyplugin1'], DummyPlugin1)
        assert 'dummyplugin2' in plugins
        assert isinstance(plugins['dummyplugin2'], DummyPlugin2)

