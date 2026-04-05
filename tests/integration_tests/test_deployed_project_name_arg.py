"""Test the --deployed-project-name CLI arg.

Skipped until django-simple-deploy fixes integration test helper `call_deploy()`:
it does `dsd_command.replace("deploy", "deploy --unit-testing")`, which replaces
every substring "deploy" — including inside `--deployed-project-name` — so the
CLI string is corrupted (e.g. `--deploy --unit-testinged-project-name`).
"""

import pytest
from tests.integration_tests.conftest import tmp_project  # noqa: F401
from tests.integration_tests.utils import manage_sample_project as msp

# Skip the default module-level `manage.py deploy call`, so we can call
# `deploy` with our own set of plugin-specific CLI args.
pytestmark = [
    pytest.mark.skip_auto_dsd_call,
    pytest.mark.skip(
        reason=(
            "call_deploy() mangles --deployed-project-name (naive replace on 'deploy'); "
            "fix in django-simple-deploy tests/integration_tests/utils/manage_sample_project.py"
        ),
    ),
]


def test_deployed_project_name_in_deploy_yml(tmp_project):
    """Kamal service/image and Postgres accessory use --deployed-project-name."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100 --deployed-project-name prod_blog"
    msp.call_deploy(tmp_project, cmd)

    path = tmp_project / "config" / "deploy.yml"
    contents = path.read_text()
    assert "service: prod_blog" in contents
    assert "image: prod_blog" in contents
    assert "POSTGRES_USER: prod_blog" in contents
    assert "POSTGRES_DB: prod_blog" in contents


def test_deployed_project_name_in_kamal_secrets(tmp_project):
    """DATABASE_URL uses kamal app name from --deployed-project-name."""
    cmd = "python manage.py deploy --ip-address 192.168.1.100 --deployed-project-name prod_blog"
    msp.call_deploy(tmp_project, cmd)

    secrets_path = tmp_project / ".kamal" / "secrets"
    contents = secrets_path.read_text()
    for line in contents.splitlines():
        if line.startswith("DATABASE_URL="):
            assert line.startswith("DATABASE_URL=postgres://prod_blog:")
            assert "@prod_blog-postgres:5432/prod_blog" in line
            break
    else:
        raise AssertionError("DATABASE_URL= line not found in .kamal/secrets")
