"""Test the --host CLI arg."""

import pytest

from tests.integration_tests.conftest import tmp_project
from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = pytest.mark.skip_auto_dsd_call


def test_host_written_to_deploy_yml(tmp_project):
    """Test that --host is written to the proxy section of deploy.yml."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100 --host foo.example.com"
    msp.call_deploy(tmp_project, cmd)

    path = tmp_project / "config" / "deploy.yml"
    contents = path.read_text()
    assert "host: foo.example.com" in contents

    # Verify host is inside the proxy section.
    lines = contents.splitlines()
    proxy_index = lines.index("proxy:")
    host_index = next(i for i, l in enumerate(lines) if "host: foo.example.com" in l)
    assert host_index > proxy_index
    assert lines[host_index].startswith("  ")


def test_host_written_to_settings(tmp_project):
    """Test that --host is written to ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS in settings.py."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100 --host foo.example.com"
    msp.call_deploy(tmp_project, cmd)

    path = tmp_project / "blog" / "settings.py"
    contents = path.read_text()
    assert 'ALLOWED_HOSTS = ["192.168.1.100", "foo.example.com"]' in contents
    assert 'CSRF_TRUSTED_ORIGINS = ["https://192.168.1.100", "https://foo.example.com"]' in contents
