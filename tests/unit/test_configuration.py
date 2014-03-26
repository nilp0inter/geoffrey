import os
import geoffrey
from tempfile import TemporaryDirectory


def test_autocreate_conf():
    """Autocreate main configuration if missing."""

    with TemporaryDirectory() as tempdir:
        config_file = os.path.join(tempdir, 'geoffrey.conf')
        geoffrey.Server.read_main_config(config_file)
        assert os.path.exists(config_file)
        assert os.path.isfile(config_file)


def test_server_projects():
    """The server knows its active projects."""

    fake_projects = ['project1', 'project2']

    with TemporaryDirectory() as tempdir:

        # Create the fake config structure
        config_file = os.path.join(tempdir, 'geoffrey.conf')
        for project in fake_projects:
            fake_project_dir = os.path.join(tempdir, 'projects', project)
            os.makedirs(fake_project_dir)
            with open(os.path.join(fake_project_dir,
                                   '{}.conf'.format(project)), 'w') as f:
                f.write('[project]\n\n')

        # Create the server, read the config and test project existence
        server = geoffrey.Server(config=config_file)
        for project in fake_projects:
            assert project in server.projects
