"""Manages all VPS Kamal-specific aspects of the deployment process.

Notes:
- 

Add a new file to the user's project, without using a template:

    def _add_dockerignore(self):
        # Add a dockerignore file, based on user's local project environmnet.
        path = dsd_config.project_root / ".dockerignore"
        dockerignore_str = self._build_dockerignore()
        plugin_utils.add_file(path, dockerignore_str)

Add a new file to the user's project, using a template:

    def _add_dockerfile(self):
        # Add a minimal dockerfile.
        template_path = self.templates_path / "dockerfile_example"
        context = {
            "django_project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        # Write file to project.
        path = dsd_config.project_root / "Dockerfile"
        plugin_utils.add_file(path, contents)

Modify user's settings file:

    def _modify_settings(self):
        # Add platformsh-specific settings.
        template_path = self.templates_path / "settings.py"
        context = {
            "deployed_project_name": self._get_deployed_project_name(),
        }
        plugin_utils.modify_settings_file(template_path, context)

Add a set of requirements:

    def _add_requirements(self):
        # Add requirements for deploying to Fly.io.
        requirements = ["gunicorn", "psycopg2-binary", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(requirements)
"""

import subprocess
import sys, os, re, json
from pathlib import Path

from django.utils.safestring import mark_safe

import requests

from . import deploy_messages as platform_msgs
from .plugin_config import plugin_config

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError


class PlatformDeployer:
    """Perform the initial deployment to VPS Kamal

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and ...
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to VPS Kamal...")

        self._validate_platform()
        self._prep_automate_all()
        
        self._add_deploy_yml()

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to VPS Kamal.

        Returns:
            None
        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        if not dsd_config.automate_all:
            return

        ip = plugin_config.ip_address
        cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
               f"root@{ip}", "echo", "ok"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            raise DSDCommandError(
                f"SSH connection to {ip} timed out."
                f" Ensure the server is reachable and SSH key auth is configured."
            )

        if result.returncode != 0:
            msg = f"Could not connect to {ip} via SSH."
            msg += f"\n  Ensure you can run: ssh root@{ip}"
            msg += f"\n  stderr: {result.stderr.strip()}"
            raise DSDCommandError(msg)


    def _add_deploy_yml(self):
        """Add a Kamal config/deploy.yml file."""
        template_path = self.templates_path / "deploy.yml"
        context = {
            "project_name": dsd_config.local_project_name,
            "ip_address": plugin_config.ip_address or "REPLACE_WITH_SERVER_IP",
            "host": plugin_config.host or "",
        }
        contents = plugin_utils.get_template_string(template_path, context)

        path = dsd_config.project_root / "config" / "deploy.yml"
        path.parent.mkdir(exist_ok=True)
        plugin_utils.add_file(path, contents)

    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass


    def _conclude_automate_all(self):
        """Finish automating the push to VPS Kamal.

        - Commit all changes.
        - ...
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying to VPS Kamal...")

        # Should set self.deployed_url, which will be reported in the success message.
        pass

    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if dsd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=dsd_config.log_output)
        plugin_utils.write_output(msg)
