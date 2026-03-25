"""Config class for plugin information shared with core."""

from . import deploy_messages as platform_msgs


class PluginConfig:
    """Class for managing attributes that need to be shared with core.

    This is similar to the class SDConfig in core's sd_config.py.

    This should future-proof plugins somewhat, in that if more information needs
    to be shared back to core, it can be added here without breaking changes to the
    core-plugin interface.

    Get plugin-specific attributes required by core.

    Required:
    - automate_all_supported
    - platform_name
    Optional:
    - confirm_automate_all_msg (required if automate_all_supported is True)
    """

    def __init__(self):
        self.automate_all_supported = True
        self.confirm_automate_all_msg = platform_msgs.confirm_automate_all
        self.platform_name = "VPS via Kamal"

        self.ip_address = None
        self.host = None
        self.use_sqlite = False
        self.kamal_cmd = None

# Create plugin_config once right here. This approach keeps from having to pass the config
# instance between core, plugins, and these utility functions.
plugin_config = PluginConfig()
