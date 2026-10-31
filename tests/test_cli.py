import pytest

from oscar_patterns import __version__
from oscar_patterns.cli import main


def test_no_arguments_shows_help(capsys):
    assert main([]) == 0
    assert "Data pipeline commands are not yet available." in capsys.readouterr().out


def test_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--help"])
    assert result.value.code == 0
    assert "--version" in capsys.readouterr().out


def test_version_matches_package(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--version"])
    assert result.value.code == 0
    assert capsys.readouterr().out.strip() == f"oscar-data {__version__}"


@pytest.mark.parametrize("command", ["ingest", "train", "export-public"])
def test_unimplemented_commands_are_rejected(command, capsys):
    with pytest.raises(SystemExit) as result:
        main([command])
    assert result.value.code == 2
    assert f"unrecognized arguments: {command}" in capsys.readouterr().err
