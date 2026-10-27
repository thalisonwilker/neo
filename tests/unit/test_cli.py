from typer.testing import CliRunner

from neo.cli import __version__, app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Neo — Personal Command Assistant" in result.output
    assert "config" in result.output


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"Neo v{__version__}" in result.output
