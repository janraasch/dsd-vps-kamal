"""Extends the core django-simple-deploy CLI."""

import ipaddress

from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config

from .plugin_config import plugin_config


class PluginCLI:
    def __init__(self, parser):
        """Add plugin-specific args."""
        group_desc = "Plugin-specific CLI args for dsd-vps-kamal"
        plugin_group = parser.add_argument_group(
            title="Options for dsd-vps-kamal",
            description=group_desc,
        )

        plugin_group.add_argument(
            "--ip-address",
            type=str,
            help="IP address of the VPS to deploy to.",
            default=None,
        )

        plugin_group.add_argument(
            "--host",
            type=str,
            help="Host name for Kamal proxy routing (e.g. myapp.example.com).",
            default=None,
        )

        plugin_group.add_argument(
            "--sqlite",
            action="store_true",
            help="Use SQLite instead of PostgreSQL for the database.",
            default=False,
        )


def validate_cli(options):
    """Validate options that were passed to CLI."""
    ip_address = options["ip_address"]
    _validate_ip_address(ip_address)

    host = options["host"]
    if host:
        plugin_config.host = host

    plugin_config.use_sqlite = options["sqlite"]


# --- Helper functions ---


def _validate_ip_address(ip_address):
    """Validate the IP address arg that was passed."""
    if not ip_address:
        if dsd_config.unit_testing:
            return
        msg = "The --ip-address argument is required."
        raise DSDCommandError(msg)

    try:
        ipaddress.IPv4Address(ip_address)
    except ipaddress.AddressValueError as e:
        msg = f"The --ip-address value '{ip_address}' is not a valid IPv4 address."
        raise DSDCommandError(msg) from e

    # ip_address is valid. Set the relevant plugin_config attribute.
    plugin_config.ip_address = ip_address
