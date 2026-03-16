"""Test the help output when dsd-vps-kamal is installed.

The core django-simple-deploy library tests its own help output.
This test checks that plugin-specific options are included in the help output.
"""

# from pathlib import Path

import pytest

# from tests.integration_tests.conftest import tmp_project
# from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = pytest.mark.skip_auto_dsd_call


# def test_plugin_help_output(tmp_project, request):
#     """Test that dsd-vps-kamal CLI args are included in help output.

#     Note: When updating this, run `manage.py deploy --help` in a terminal set
#     to 80 characters wide. That splits help text at the same places as the
#     test environment.
#     On macOS, you can simply run:
#         $ COLUMNS=80 python manage.py deploy --help
#     """
#     cmd = "python manage.py deploy --help"
#     stdout, stderr = msp.call_deploy(tmp_project, cmd)

#     path_reference = Path(__file__).parent / "reference_files" / "plugin_help_text.txt"
#     help_lines = path_reference.read_text().splitlines()

#     for line in help_lines:
#         assert line in stdout
