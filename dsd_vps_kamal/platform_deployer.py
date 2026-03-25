"""Manages all Kamal-powered VPS-specific aspects of the deployment process.
"""

import subprocess
import sys, os, re, json
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

import requests

from . import deploy_messages as platform_msgs
from .plugin_config import plugin_config

from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import DSDCommandError


class PlatformDeployer:
    """Perform the initial deployment to a VPS powered by Kamal

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and run `kamal setup`.
    """

    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        """Coordinate the overall configuration and deployment."""
        plugin_utils.write_output("\nConfiguring project for deployment to VPS using Kamal...")

        self._validate_platform()
        self._prep_automate_all()

        self._modify_gitignore()
        self._add_kamal_secrets()
        self._add_deploy_yml()
        self._add_dockerignore()
        self._add_dockerfile()
        self._add_start_script()
        self._add_requirements()
        self._modify_settings()

        self._conclude_automate_all()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to a VPS powered by Kamal.

        Make sure Kamal is installed. 
        Make sure the VPS is reachable via SSH.

        Returns:
            None
        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        self._check_vps_kamal_settings()

        if not dsd_config.automate_all:
            return

        ip = plugin_config.ip_address
        self._check_ssh_connection(ip)

        self._validate_cli()
        self._check_docker_daemon()

    def _check_docker_daemon(self):
        """Check that the Docker daemon is running."""
        try:
            output_obj = plugin_utils.run_quick_command("docker info")
        except FileNotFoundError:
            raise DSDCommandError(platform_msgs.docker_not_running)

        plugin_utils.log_info(output_obj)

        if output_obj.returncode:
            raise DSDCommandError(platform_msgs.docker_not_running)

    def _validate_cli(self):
        """Validate that Kamal is installed.

        Checks for Kamal in two ways:
        1. Directly via `kamal version` (standard gem install).
        2. Via rv's `rvx kamal version` (rv tool-managed install).

        Stores the working command prefix on plugin_config.kamal_cmd so the
        rest of the plugin can invoke Kamal correctly.
        """
        for cmd_prefix in ("kamal", "rvx kamal"):
            cmd = f"{cmd_prefix} version"
            try:
                output_obj = plugin_utils.run_quick_command(cmd)
            except FileNotFoundError:
                continue

            plugin_utils.log_info(output_obj)

            if output_obj.returncode:
                continue

            plugin_config.kamal_cmd = cmd_prefix
            return

        raise DSDCommandError(platform_msgs.cli_not_installed)

    def _check_ssh_connection(self, ip):
        """Check that the target VPS is reachable via SSH."""
        cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
               "-o", "StrictHostKeyChecking=accept-new",
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

    def _check_vps_kamal_settings(self):
        """Check to see if a VPS Kamal settings block already exists."""
        start_line = "# VPS Kamal settings."
        plugin_utils.check_settings(
            "# VPS Kamal settings.",
            start_line,
            platform_msgs.vps_kamal_settings_found,
            platform_msgs.cant_overwrite_settings,
        )

    def _add_deploy_yml(self):
        """Add a Kamal config/deploy.yml file."""
        template_path = self.templates_path / "deploy.yml"
        context = {
            "app_name": dsd_config.local_project_name,
            "ip_address": plugin_config.ip_address or "__SERVER_IP__",
            "host": plugin_config.host or "",
        }
        contents = plugin_utils.get_template_string(template_path, context)
        contents = plugin_utils.remove_doubled_blank_lines(contents)

        path = dsd_config.project_root / "config" / "deploy.yml"
        path.parent.mkdir(exist_ok=True)
        plugin_utils.add_file(path, contents)

    def _modify_gitignore(self):
        """Add .kamal/secrets to .gitignore."""
        gitignore_path = dsd_config.git_path / ".gitignore"
        pattern = ".kamal/secrets"

        if not gitignore_path.exists():
            gitignore_path.write_text(f"{pattern}\n", encoding="utf-8")
            plugin_utils.write_output(f"Created .gitignore with {pattern}")
            return

        contents = gitignore_path.read_text()
        if pattern not in contents:
            contents += f"\n{pattern}\n"
            gitignore_path.write_text(contents)
            plugin_utils.write_output(f"Added {pattern} to .gitignore")

    def _add_kamal_secrets(self):
        """Create .kamal/secrets with generated credentials."""
        secret_key = get_random_secret_key()
        postgres_password = get_random_string(length=24)
        app_name = dsd_config.local_project_name

        database_url = (
            f"postgres://{app_name}:{postgres_password}"
            f"@{app_name}-postgres:5432/{app_name}"
        )

        # mark_safe is required here because Django's template engine auto-escapes
        # by default. Generated secrets can contain <, >, &, etc. which would be
        # mangled into &lt;, &gt;, &amp; without mark_safe.
        template_path = self.templates_path / "kamal_secrets"
        context = {
            "secret_key": mark_safe(secret_key),
            "database_url": mark_safe(database_url),
            "postgres_password": mark_safe(postgres_password),
        }
        contents = plugin_utils.get_template_string(template_path, context)

        path = dsd_config.project_root / ".kamal" / "secrets"
        path.parent.mkdir(exist_ok=True)
        plugin_utils.add_file(path, contents)

    def _add_dockerfile(self):
        """Add a Dockerfile for building the deployment image."""
        template_path = self.templates_path / "dockerfile"
        context = {
            "django_project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        path = dsd_config.project_root / "Dockerfile"
        plugin_utils.add_file(path, contents)

    def _add_dockerignore(self):
        """Add a .dockerignore file for a clean and secure build context."""
        template_path = self.templates_path / "dockerignore"
        contents = plugin_utils.get_template_string(template_path, {})

        path = dsd_config.project_root / ".dockerignore"
        plugin_utils.add_file(path, contents)

    def _add_start_script(self):
        """Add start-web.sh script that runs migrations then starts gunicorn."""
        template_path = self.templates_path / "start-web.sh"
        context = {
            "django_project_name": dsd_config.local_project_name,
        }
        contents = plugin_utils.get_template_string(template_path, context)

        path = dsd_config.project_root / "start-web.sh"
        plugin_utils.add_file(path, contents)

    def _add_requirements(self):
        """Add requirements for deploying to VPS via Kamal."""
        requirements = ["gunicorn", "psycopg2-binary", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(requirements)

    def _modify_settings(self):
        """Add VPS Kamal-specific settings."""
        template_path = self.templates_path / "settings.py"
        context = {
            "ip_address": plugin_config.ip_address or "__SERVER_IP__",
            "host": plugin_config.host or "",
            "settings_module_path": f"{dsd_config.local_project_name}.settings",
        }
        plugin_utils.modify_settings_file(template_path, context)

    def _prep_automate_all(self):
        """Take any further actions needed if using automate_all."""
        pass


    def _conclude_automate_all(self):
        """Finish automating the push to VPS Kamal.

        - Commit all changes.
        - Run `kamal setup`.
        - Set deployed URL.
        """
        # Making this check here lets deploy() be cleaner.
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        # Push project.
        plugin_utils.write_output("  Deploying to VPS using Kamal...")
        kamal_cmd = plugin_config.kamal_cmd
        plugin_utils.run_slow_command(f"{kamal_cmd} setup")
        # plugin_utils.run_slow_command(f"{kamal_cmd} deploy")

        if plugin_config.host:
            self.deployed_url = f"https://{plugin_config.host}"
        else:
            self.deployed_url = f"http://{plugin_config.ip_address}"

    def _show_success_message(self):
        """After a successful run, show a message about what to do next.

        Describe ongoing approach of commit, push, migrate.
        """
        if dsd_config.automate_all:
            msg = platform_msgs.success_msg_automate_all(self.deployed_url)
        else:
            msg = platform_msgs.success_msg(log_output=dsd_config.log_output)
        plugin_utils.write_output(msg)
