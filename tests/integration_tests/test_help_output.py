"""Test the help output when dsd-vps-kamal is installed.

The core django-simple-deploy library tests its own help output.
This test checks that plugin-specific options are included in the help output.
"""

import pytest
from tests.integration_tests.conftest import tmp_project  # noqa: F401
from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = pytest.mark.skip_auto_dsd_call


def test_plugin_help_output(tmp_project, request):
    """Test that dsd-vps-kamal CLI args are included in help output."""
    cmd = "python manage.py deploy --help"
    stdout, stderr = msp.call_deploy(tmp_project, cmd)

    # Verify the full plugin-specific help section appears in the output.
    # Note: When updating this, run `manage.py deploy --help` in a terminal set
    # to 80 characters wide. On macOS: COLUMNS=80 python manage.py deploy --help
    expected = (
        "Options for dsd-vps-kamal:\n"
        "  Plugin-specific CLI args for dsd-vps-kamal\n"
        "\n"
        "  --ip-address IP       IP address of the VPS to deploy to (e.g. 203.0.113.1).\n"
        "  --host HOST           Host name for Kamal proxy routing (e.g.\n"
        "                        myapp.example.com).\n"
        "  --sqlite              Use SQLite instead of PostgreSQL for the database."
    )
    assert expected in stdout
