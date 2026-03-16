"""Manages all VPS Kamal-specific aspects of the deployment process.

Notes:
- ...
"""

import django_simple_deploy

from dsd_vps_kamal.platform_deployer import PlatformDeployer
from .plugin_config import plugin_config
from .cli import PluginCLI, validate_cli


@django_simple_deploy.hookimpl
def dsd_get_plugin_config():
    """Get platform-specific attributes needed by core."""
    return plugin_config


@django_simple_deploy.hookimpl
def dsd_get_plugin_cli(parser):
    """Get plugin's CLI extension."""
    plugin_cli = PluginCLI(parser)


@django_simple_deploy.hookimpl
def dsd_validate_cli(options):
    """Validate and parse plugin-specific CLI args."""
    validate_cli(options)


@django_simple_deploy.hookimpl
def dsd_deploy():
    """Carry out platform-specific deployment steps."""
    platform_deployer = PlatformDeployer()
    platform_deployer.deploy()
