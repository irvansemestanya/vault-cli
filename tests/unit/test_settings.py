from __future__ import unicode_literals

import io

from vault_cli import settings


def test_read_config_file_not_existing():
    assert settings.read_config_file("/non-existant-file") is None


def test_read_config_file(tmpdir):
    path = str(tmpdir.join("test.yml"))
    open(path, "w").write('{"yay": 1}')

    assert settings.read_config_file(path) == {"yay": 1}


def test_dash_to_underscores():
    result = settings.dash_to_underscores(
        {"a": "b", "c_d": "e_f", "g-h": "i-j"})
    expected = {"a": "b", "c_d": "e_f", "g_h": "i-j"}
    assert result == expected


def test_read_all_files_no_file():
    d = {"token": "yay", "certificate": "yo", "password": "aaa"}
    assert settings.read_all_files(d) == d


def test_read_all_files(tmpdir):
    token_path = str(tmpdir.join("token"))
    open(token_path, "wb").write(b'yay')
    certificate_path = str(tmpdir.join("certificate"))
    open(certificate_path, "wb").write(b'yo')
    password_path = str(tmpdir.join("password"))
    open(password_path, "wb").write(b'aaa')

    d = {"token_file": token_path,
         "certificate_file": certificate_path,
         "password_file": password_path}
    expected = {"token": "yay", "certificate": "yo", "password": "aaa"}
    assert settings.read_all_files(d) == expected


def test_read_file_no_path():
    assert settings.read_file(None) is None


def test_read_file_stdin(mocker):
    mocker.patch("sys.stdin", io.StringIO("yay"))
    assert settings.read_file("-") == "yay"


def test_build_config_from_files(mocker):
    config_file = {"test-a": "b"}
    mocker.patch("vault_cli.settings.read_config_file",
                 return_value=config_file)
    read_all_files = mocker.patch("vault_cli.settings.read_all_files",
                                  side_effect=lambda x: x)

    result = settings.build_config_from_files(["a"])

    assert result["test_a"] == "b"
    assert "url" in result
    assert read_all_files.called is True


def test_build_config_from_files_no_files(mocker):
    mocker.patch("vault_cli.settings.read_config_file",
                 return_value=None)

    result = settings.build_config_from_files(["a"])

    assert result == settings.DEFAULTS


def test_get_vault_options(config):
    config.update({"a": "b"})

    assert settings.get_vault_options(c="d") == {"a": "b", "c": "d"}
