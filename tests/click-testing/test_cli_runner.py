import pytest
from click.testing import CliRunner
from unittest.mock import patch

from app.cli import cli
from app.commands import check, download, progress, setup, verify, version


class TestClickRunner:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture(autouse=True)
    def setup_cli_commands(self):
        """Register commands to the CLI before each test"""
        commands = [check, download, progress, setup, verify, version]
        for command in commands:
            if command.name not in cli.commands:
                cli.add_command(command)
        yield
        # Cleanup after test
        for command in commands:
            if command.name in cli.commands:
                cli.commands.pop(command.name)

    @pytest.fixture(autouse=True)
    def mock_version_check(self):
        """Mock version check to avoid network calls"""
        with patch("app.cli.requests.get") as mock_get:
            mock_get.return_value.headers = {
                "Location": "https://github.com/git-mastery/app/releases/tag/v1.0.0"
            }
            yield mock_get

    def test_cli_help_contains_main_commands(self, runner):
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        for command in ["check", "download", "progress", "setup", "verify", "version"]:
            assert command in result.output

    def test_version_command_output(self, runner):
        result = runner.invoke(cli, ["version"])

        assert result.exit_code == 0
        assert "Git-Mastery app is" in result.output
