"""Extends the core django-simple-deploy CLI."""

import ipaddress

from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)

from .plugin_config import plugin_config


class PluginCLI:

    def __init__(self, parser):
        """Add plugin-specific args."""
        group_desc = "Plugin-specific CLI args for dsd-vps-kamal"
        plugin_group = parser.add_argument_group(
            title="Options for dsd-vps-kamal",
            description = group_desc,
        )

        plugin_group.add_argument(
            "--ip-address",
            type=str,
            help="IP address of the VPS to deploy to.",
            default=None,
        )


def validate_cli(options):
    """Validate options that were passed to CLI."""
    ip_address = options["ip_address"]
    _validate_ip_address(ip_address)


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
    except ipaddress.AddressValueError:
        msg = f"The --ip-address value '{ip_address}' is not a valid IPv4 address."
        raise DSDCommandError(msg)

    # ip_address is valid. Set the relevant plugin_config attribute.
    plugin_config.ip_address = ip_address
