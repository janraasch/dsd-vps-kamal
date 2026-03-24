import time

import pytest

from tests.e2e_tests.utils import it_helper_functions as it_utils
from . import utils as platform_utils

from tests.e2e_tests.conftest import tmp_project, cli_options


# --- Test functions ---


# For normal test runs, skip this test.
# When working on setup steps, skip other tests and run this one.
#   This will force the tmp_project fixture to run, without doing a full deployment.
@pytest.mark.skip
def test_dummy(tmp_project, request):
    """Helpful to have an empty test to run when testing setup steps."""
    pass


# Skip this test and enable test_dummy() to speed up testing of setup steps.
# @pytest.mark.skip
def test_deployment(tmp_project, cli_options, request):
    """Test the full, live deployment process to VPS Kamal."""

    # Cache the platform name for teardown work.
    request.config.cache.set("platform", "dsd_vps_kamal")

    print("\nTesting deployment to VPS Kamal using the following options:")
    print(cli_options.__dict__)

    python_cmd = it_utils.get_python_exe(tmp_project)

    # Create the Hetzner server; cache the IP for teardown.
    server_ip = platform_utils.create_project()
    request.config.cache.set("app_name", server_ip)

    # Run simple_deploy against the test project, passing the server IP.
    it_utils.run_simple_deploy(
        python_cmd,
        automate_all=cli_options.automate_all,
        plugin_args_string=f"--ip-address {server_ip}",
    )

    # If testing Pipenv, lock after adding new packages.
    if cli_options.pkg_manager == "pipenv":
        it_utils.make_sp_call(f"{python_cmd} -m pipenv lock")

    project_url = f"http://{server_ip}"

    # Pause to let Kamal finish starting the app.
    print("\nPausing 10s to let deployment finish...")
    time.sleep(10)

    remote_functionality_passed = it_utils.check_deployed_app_functionality(
        python_cmd, project_url
    )
    local_functionality_passed = it_utils.check_local_app_functionality(python_cmd)
    log_check_passed = platform_utils.check_log(tmp_project)

    it_utils.summarize_results(
        remote_functionality_passed,
        local_functionality_passed,
        cli_options,
        tmp_project,
    )

    # Make final assertions, so pytest results are meaningful.
    assert remote_functionality_passed
    assert local_functionality_passed
    assert log_check_passed
