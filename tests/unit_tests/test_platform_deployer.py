"""Unit tests for PlatformDeployer.

Tests SSH connectivity validation and secrets file creation,
following the pythonanywhere pattern.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError

from dsd_vps_kamal.platform_deployer import PlatformDeployer, dsd_config
from dsd_vps_kamal.plugin_config import plugin_config


def test_validate_platform_skipped_without_automate_all(monkeypatch):
    """_validate_platform is skipped when automate_all is False."""
    monkeypatch.setattr(dsd_config, "automate_all", False)

    deployer = PlatformDeployer()
    # Should not raise any exception, even without an IP configured.
    deployer._validate_platform()


def test_validate_platform_ssh_succeeds(monkeypatch, mocker):
    """_validate_platform succeeds when SSH connection works."""
    monkeypatch.setattr(dsd_config, "automate_all", True)
    monkeypatch.setattr(plugin_config, "ip_address", "192.168.1.100")

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=0)

    deployer = PlatformDeployer()
    deployer._validate_platform()

    mock_run.assert_called_once_with(
        ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
         "root@192.168.1.100", "echo", "ok"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_validate_platform_ssh_fails(monkeypatch, mocker):
    """_validate_platform raises error when SSH connection fails."""
    monkeypatch.setattr(dsd_config, "automate_all", True)
    monkeypatch.setattr(plugin_config, "ip_address", "192.168.1.100")

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.return_value = mocker.Mock(returncode=255, stderr="Permission denied")

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError, match="Could not connect"):
        deployer._validate_platform()


def test_validate_platform_ssh_timeout(monkeypatch, mocker):
    """_validate_platform raises error when SSH connection times out."""
    monkeypatch.setattr(dsd_config, "automate_all", True)
    monkeypatch.setattr(plugin_config, "ip_address", "192.168.1.100")

    mock_run = mocker.patch("dsd_vps_kamal.platform_deployer.subprocess.run")
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="ssh", timeout=10)

    deployer = PlatformDeployer()
    with pytest.raises(DSDCommandError, match="timed out"):
        deployer._validate_platform()


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
