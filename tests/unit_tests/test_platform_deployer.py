"""Unit tests for PlatformDeployer._validate_platform().

Tests SSH connectivity validation following the pythonanywhere pattern.
"""

import subprocess

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
