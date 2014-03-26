import os


def test_autocreate_doc():
    from tempfile import TemporaryDirectory
    import geoffrey

    with TemporaryDirectory() as tempdir:
        config_file = os.path.join(tempdir, 'geoffrey.conf')
        geoffrey.read_main_config(config_file)
        assert os.path.exists(config_file)
        assert os.path.isfile(config_file)
