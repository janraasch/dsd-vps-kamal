"""Test the --ip-address CLI arg."""

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


def test_ip_address_in_settings(tmp_project):
    """Test that a valid IP address is written to settings.py."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100"
    msp.call_deploy(tmp_project, cmd)

    path = tmp_project / "blog" / "settings.py"
    contents = path.read_text()
    assert '"192.168.1.100"' in contents
    assert 'ALLOWED_HOSTS = ["192.168.1.100"]' in contents
    assert 'CSRF_TRUSTED_ORIGINS = ["https://192.168.1.100"]' in contents


def test_invalid_ip_address(tmp_project):
    """Test that an invalid IP address raises an error."""
    cmd = "python manage.py deploy --ip-address not-an-ip"
    stdout, stderr = msp.call_deploy(tmp_project, cmd)

    assert "not a valid" in stderr.lower() or "invalid" in stderr.lower()
