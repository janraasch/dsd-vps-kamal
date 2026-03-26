"""A collection of messages used during the configuration and deployment process."""

# For conventions, see documentation in core deploy_messages.py

from textwrap import dedent

from django.conf import settings


confirm_automate_all = """
The --automate-all flag means django-simple-deploy will:
- ...
- Commit all changes to your project that are necessary for deployment with Kamal.
- Run `kamal setup` to setup your VPS for deployment.
- Run `kamal deploy` to deploy your project to your VPS.
- Open your deployed project in a new browser tab.
"""

cancel_vpskamal = """
Okay, cancelling VPS configuration and deployment.
"""

cli_not_installed = """
In order to deploy to your VPS using Kamal, you need to install the Kamal CLI.
  You can install it directly as a Ruby gem:
    $ gem install kamal
  Or via rv (https://github.com/spinel-coop/rv):
    $ rv tool install kamal
  See also: https://kamal-deploy.org/docs/installation/
After installing the CLI, you can run the deploy command again.
"""

docker_not_running = """
The Docker daemon does not appear to be running. Kamal needs Docker to
build and push your project's container image.
  Please start Docker and then run the deploy command again.
"""

# TODO: Do we need this? Or maybe we can check here that we can access the VPS via SSH?
cli_logged_out = """
You are currently logged out of the VPS Kamal CLI. Please log in,
  and then run the deploy command again.
You can log in from  the command line:
  $ ...
"""

vps_kamal_settings_found = """
There is already a VPS Kamal-specific settings block in settings.py. Is it okay to
overwrite this block, and everything that follows in settings.py?
"""

cant_overwrite_settings = """
In order to configure the project for deployment, we need to write a VPS Kamal-specific
settings block. Please remove the current VPS Kamal-specific settings, and then run
the deploy command again.
"""


# --- Dynamic strings ---
# These need to be generated in functions, to display information that's determined as
# the script runs.


def success_msg(log_output=""):
    """Success message, for configuration-only run.

    Note: This is immensely helpful; I use it just about every time I do a
      manual test run.
    """

    msg = dedent(
        f"""
        --- Your project is now configured for deployment on VPS Kamal ---

        To deploy your project, you will need to:
        - Commit the changes made in the configuration process.
            $ git status
            $ git add .
            $ git commit -am "Configured project for deployment."
        - Push your project to VPS Kamal's servers:
            $ ...
        - Open your project:
            $ ...    
        - As you develop your project further:
            - Make local changes
            - Commit your local changes
            - Run `kamal deploy` again to push your changes.
    """
    )

    if log_output:
        msg += dedent(
            f"""
        - You can find a full record of this configuration in the dsd_logs directory.
        """
        )

    return msg


def success_msg_automate_all(deployed_url):
    """Success message, when using --automate-all."""

    msg = dedent(
        f"""

        --- Your project should now be deployed on VPS Kamal ---

        It should have opened up in a new browser tab. If you see a
          "server not available" message, wait a minute or two and
          refresh the tab. It sometimes takes a few minutes for the
          server to be ready.
        - You can also visit your project at {deployed_url}

        If you make further changes and want to push them to VPS Kamal,
        commit your changes and then run `...`.
    """
    )
    return msg
