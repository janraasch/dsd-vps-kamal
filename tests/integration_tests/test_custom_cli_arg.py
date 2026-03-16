"""Test a custom plugin-specific CLI arg."""

import pytest

from tests.integration_tests.conftest import tmp_project
from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = pytest.mark.skip_auto_dsd_call


# def test_vm_size_arg(tmp_project, request):
#     """Test that a custom vm size is written to fly.toml."""
#     cmd = "python manage.py deploy --vm-size shared-cpu-2x"
#     msp.call_deploy(tmp_project, cmd, platform="fly_io")

#     path = tmp_project / "fly.toml"
#     contents_fly_toml = path.read_text()

#     assert 'size = "shared-cpu-2x"' in contents_fly_toml
