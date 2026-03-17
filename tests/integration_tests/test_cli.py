"""Test the --ip-address custom CLI arg."""

import pytest

from tests.integration_tests.conftest import tmp_project
from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = pytest.mark.skip_auto_dsd_call


def test_valid_ip_address(tmp_project):
    """Test that a valid IP address is accepted without error."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100"
    stdout, stderr = msp.call_deploy(tmp_project, cmd)

    assert "invalid" not in stderr.lower()
    assert "error" not in stderr.lower()


def test_invalid_ip_address(tmp_project):
    """Test that an invalid IP address raises an error."""
    cmd = "python manage.py deploy --ip-address not-an-ip"
    stdout, stderr = msp.call_deploy(tmp_project, cmd)

    assert "not a valid" in stderr.lower() or "invalid" in stderr.lower()
