"""Unit tests for PlatformDeployer.

Tests SSH connectivity validation and secrets file creation,
following the pythonanywhere pattern.
"""

import subprocess
import sys

import pytest
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError

from dsd_vps_kamal.platform_deployer import PlatformDeployer, dsd_config
from dsd_vps_kamal.plugin_config import plugin_config
from dsd_vps_kamal import deploy_messages as platform_msgs


def test_validate_platform_skipped_when_unit_testing(monkeypatch):
    """_validate_platform is skipped when unit_testing is True."""
    monkeypatch.setattr(dsd_config, "unit_testing", True)

    deployer = PlatformDeployer()
    # Should not raise any exception, even without an IP configured.
    deployer._validate_platform()


def test_check_vps_kamal_settings_calls_check_settings(mocker):
    """_check_vps_kamal_settings calls check_settings with expected args."""
    mock_check = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.check_settings")

    deployer = PlatformDeployer()
    deployer._check_vps_kamal_settings()

    mock_check.assert_called_once_with(
        "# VPS Kamal settings.",
        "# VPS Kamal settings.",
        platform_msgs.vps_kamal_settings_found,
        platform_msgs.cant_overwrite_settings,
    )


def test_check_ssh_connection_succeeds(mocker):
    """_check_ssh_connection succeeds when SSH connection works."""
    ip = "192.168.1.100"

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=0)

    deployer = PlatformDeployer()
    deployer._check_ssh_connection(ip)

    mock_run.assert_called_once_with(
        ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
         "root@192.168.1.100", "echo", "ok"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_check_ssh_connection_fails(mocker):
    """_check_ssh_connection raises error when SSH connection fails."""
    ip = "192.168.1.100"

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=255, stderr="Permission denied")

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError, match="Could not connect"):
        deployer._check_ssh_connection(ip)


def test_check_ssh_connection_timeout(mocker):
    """_check_ssh_connection raises error when SSH connection times out."""
    ip = "192.168.1.100"

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="ssh", timeout=10)

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError, match="timed out"):
        deployer._check_ssh_connection(ip)


# --- Tests for _modify_gitignore ---


def test_modify_gitignore_adds_kamal_secrets(tmp_path, monkeypatch):
    """_modify_gitignore adds .kamal/secrets to existing .gitignore."""
    monkeypatch.setattr(dsd_config, "git_path", tmp_path)
    monkeypatch.setattr(dsd_config, "stdout", sys.stdout)

    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n")

    deployer = PlatformDeployer()
    deployer._modify_gitignore()

    contents = gitignore.read_text()
    assert ".kamal/secrets" in contents


def test_modify_gitignore_no_duplicate(tmp_path, monkeypatch):
    """_modify_gitignore doesn't duplicate if already present."""
    monkeypatch.setattr(dsd_config, "git_path", tmp_path)
    monkeypatch.setattr(dsd_config, "stdout", sys.stdout)

    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n.kamal/secrets\n")

    deployer = PlatformDeployer()
    deployer._modify_gitignore()

    contents = gitignore.read_text()
    assert contents.count(".kamal/secrets") == 1


def test_modify_gitignore_creates_file(tmp_path, monkeypatch):
    """_modify_gitignore creates .gitignore if it doesn't exist."""
    monkeypatch.setattr(dsd_config, "git_path", tmp_path)
    monkeypatch.setattr(dsd_config, "stdout", sys.stdout)

    deployer = PlatformDeployer()
    deployer._modify_gitignore()

    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert ".kamal/secrets" in gitignore.read_text()


# --- Tests for _add_kamal_secrets ---


def test_add_kamal_secrets(tmp_path, monkeypatch):
    """_add_kamal_secrets creates .kamal/secrets with correct structure."""
    monkeypatch.setattr(dsd_config, "project_root", tmp_path)
    monkeypatch.setattr(dsd_config, "local_project_name", "blog")
    monkeypatch.setattr(dsd_config, "stdout", sys.stdout)
    monkeypatch.setattr(dsd_config, "unit_testing", True)

    deployer = PlatformDeployer()
    deployer._add_kamal_secrets()

    secrets_path = tmp_path / ".kamal" / "secrets"
    assert secrets_path.exists()

    contents = secrets_path.read_text()
    # Check comments are present
    assert "Secrets defined here are available for reference" in contents
    assert "git-ignored" in contents.lower() or "gitignored" in contents.lower()

    # Check all three secrets are present
    assert "SECRET_KEY=" in contents
    assert "DATABASE_URL=" in contents
    assert "POSTGRES_PASSWORD=" in contents

    # SECRET_KEY should be a generated value (not a placeholder)
    for line in contents.splitlines():
        if line.startswith("SECRET_KEY="):
            assert len(line.split("=", 1)[1]) >= 50

    # DATABASE_URL should reference app_name and postgres container
    for line in contents.splitlines():
        if line.startswith("DATABASE_URL="):
            assert line.startswith("DATABASE_URL=postgres://blog:")
            assert "@blog-postgres:5432/blog" in line

    # POSTGRES_PASSWORD should be generated (not a placeholder)
    for line in contents.splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            assert len(line.split("=", 1)[1]) >= 20


# --- Tests for _validate_cli ---


def test_validate_cli_finds_kamal_directly(mocker):
    """_validate_cli succeeds when `kamal version` works directly."""
    mock_run = mocker.patch(
        "dsd_vps_kamal.platform_deployer.plugin_utils.run_quick_command"
    )
    mock_run.return_value = mocker.Mock(returncode=0)
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.log_info")

    deployer = PlatformDeployer()
    deployer._validate_cli()

    mock_run.assert_called_once_with("kamal version")
    assert plugin_config.kamal_cmd == "kamal"


def test_validate_cli_finds_kamal_via_rvx(mocker):
    """_validate_cli falls back to `rvx kamal version` when `kamal` is not found."""
    mock_run = mocker.patch(
        "dsd_vps_kamal.platform_deployer.plugin_utils.run_quick_command"
    )
    # First call (`kamal version`) raises FileNotFoundError;
    # second call (`rvx kamal version`) succeeds.
    mock_run.side_effect = [FileNotFoundError, mocker.Mock(returncode=0)]
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.log_info")

    deployer = PlatformDeployer()
    deployer._validate_cli()

    assert mock_run.call_count == 2
    mock_run.assert_any_call("kamal version")
    mock_run.assert_any_call("rvx kamal version")
    assert plugin_config.kamal_cmd == "rvx kamal"


def test_validate_cli_finds_kamal_via_rvx_returncode(mocker):
    """_validate_cli falls back to rvx when `kamal version` returns non-zero."""
    mock_run = mocker.patch(
        "dsd_vps_kamal.platform_deployer.plugin_utils.run_quick_command"
    )
    # First call returns non-zero; second succeeds.
    mock_run.side_effect = [
        mocker.Mock(returncode=1),
        mocker.Mock(returncode=0),
    ]
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.log_info")

    deployer = PlatformDeployer()
    deployer._validate_cli()

    assert mock_run.call_count == 2
    assert plugin_config.kamal_cmd == "rvx kamal"


def test_validate_cli_neither_found(mocker):
    """_validate_cli raises DSDCommandError when neither kamal nor rvx is found."""
    mock_run = mocker.patch(
        "dsd_vps_kamal.platform_deployer.plugin_utils.run_quick_command"
    )
    mock_run.side_effect = FileNotFoundError
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.log_info")

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError):
        deployer._validate_cli()


def test_validate_cli_rvx_nonzero_returncode(mocker):
    """_validate_cli raises DSDCommandError when rvx kamal also fails."""
    mock_run = mocker.patch(
        "dsd_vps_kamal.platform_deployer.plugin_utils.run_quick_command"
    )
    mock_run.side_effect = [
        FileNotFoundError,
        mocker.Mock(returncode=1),
    ]
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.log_info")

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError):
        deployer._validate_cli()


# --- Tests for _conclude_automate_all ---


def test_conclude_automate_all_returns_when_disabled(monkeypatch, mocker):
    """_conclude_automate_all returns immediately when automate_all is False."""
    monkeypatch.setattr(dsd_config, "automate_all", False)

    mock_commit = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.commit_changes")
    mock_slow = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.run_slow_command")
    mock_write = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.write_output")

    deployer = PlatformDeployer()
    deployer._conclude_automate_all()

    mock_commit.assert_not_called()
    mock_slow.assert_not_called()
    mock_write.assert_not_called()


def test_conclude_automate_all_runs_kamal_commands_with_host(monkeypatch, mocker):
    """_conclude_automate_all commits, deploys, and opens app when automate_all is True."""
    monkeypatch.setattr(dsd_config, "automate_all", True)
    monkeypatch.setattr(plugin_config, "kamal_cmd", "kamal")
    monkeypatch.setattr(plugin_config, "host", "blog.example.com")
    monkeypatch.setattr(plugin_config, "ip_address", "192.168.1.100")

    mock_commit = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.commit_changes")
    mock_slow = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.run_slow_command")
    mock_write = mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.write_output")

    deployer = PlatformDeployer()
    deployer._conclude_automate_all()

    mock_commit.assert_called_once()
    mock_slow.assert_any_call("kamal setup")
    assert mock_slow.call_count == 1
    mock_write.assert_any_call("  Deploying to VPS using Kamal...")
    assert deployer.deployed_url == "https://blog.example.com"


def test_conclude_automate_all_uses_ip_when_host_missing(monkeypatch, mocker):
    """_conclude_automate_all sets deployed_url from ip_address if host is not set."""
    monkeypatch.setattr(dsd_config, "automate_all", True)
    monkeypatch.setattr(plugin_config, "kamal_cmd", "rvx kamal")
    monkeypatch.setattr(plugin_config, "host", None)
    monkeypatch.setattr(plugin_config, "ip_address", "192.168.1.100")

    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.commit_changes")
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.run_slow_command")
    mocker.patch("dsd_vps_kamal.platform_deployer.plugin_utils.write_output")

    deployer = PlatformDeployer()
    deployer._conclude_automate_all()

    assert deployer.deployed_url == "http://192.168.1.100"
