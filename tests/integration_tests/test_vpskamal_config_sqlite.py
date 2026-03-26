"""Integration tests for VPS Kamal with --sqlite."""

from pathlib import Path

import pytest
from tests.integration_tests.conftest import (
    dsd_version,
    pkg_manager,
    reset_test_project,
    tmp_project,
)
from tests.integration_tests.utils import it_helper_functions as hf
from tests.integration_tests.utils import manage_sample_project as msp

pytestmark = pytest.mark.skip_auto_dsd_call


@pytest.fixture(scope="module", autouse=True)
def run_sqlite_deploy(reset_test_project, tmp_project):
    """Configure the temp project with SQLite (no Postgres accessory)."""
    cmd = "python manage.py deploy --sqlite"
    msp.call_deploy(tmp_project, cmd)


def test_settings_sqlite(tmp_project):
    """settings.py uses SQLite on VPS and omits dj_database_url."""
    hf.check_reference_file(
        tmp_project,
        "blog/settings.py",
        "dsd-vps-kamal",
        reference_filename="settings_sqlite.py",
    )


def test_requirements_txt_sqlite(tmp_project, pkg_manager, tmp_path, dsd_version):
    """requirements.txt excludes Postgres-related packages when using --sqlite."""
    if pkg_manager == "req_txt":
        context = {"current-version": dsd_version}
        hf.check_reference_file(
            tmp_project,
            "requirements.txt",
            "dsd-vps-kamal",
            reference_filename="requirements_sqlite.txt",
            context=context,
            tmp_path=tmp_path,
        )
    elif pkg_manager in ["poetry", "pipenv"]:
        assert not Path("requirements.txt").exists()


def test_pyproject_toml_sqlite(tmp_project, pkg_manager, tmp_path, dsd_version):
    """Poetry deploy group omits Postgres packages when using --sqlite."""
    if pkg_manager in ("req_txt", "pipenv"):
        assert not Path("pyproject.toml").exists()
    elif pkg_manager == "poetry":
        context = {"current-version": dsd_version}
        hf.check_reference_file(
            tmp_project,
            "pyproject.toml",
            "dsd-vps-kamal",
            reference_filename="pyproject_sqlite.toml",
            context=context,
            tmp_path=tmp_path,
        )


def test_pipfile_sqlite(tmp_project, pkg_manager, tmp_path, dsd_version):
    """Pipfile omits Postgres packages when using --sqlite."""
    if pkg_manager in ("req_txt", "poetry"):
        assert not Path("Pipfile").exists()
    elif pkg_manager == "pipenv":
        context = {"current-version": dsd_version}
        hf.check_reference_file(
            tmp_project,
            "Pipfile",
            "dsd-vps-kamal",
            reference_filename="Pipfile_sqlite",
            context=context,
            tmp_path=tmp_path,
        )


def test_kamal_secrets_sqlite(tmp_project):
    """.kamal/secrets contains only SECRET_KEY when using SQLite."""
    secrets_path = tmp_project / ".kamal" / "secrets"
    assert secrets_path.exists()
    contents = secrets_path.read_text()
    assert "SECRET_KEY=" in contents
    assert "DATABASE_URL=" not in contents
    assert "POSTGRES_PASSWORD=" not in contents


def test_deploy_yml_sqlite(tmp_project):
    """config/deploy.yml has root volumes and no postgres accessory."""
    hf.check_reference_file(
        tmp_project,
        "config/deploy.yml",
        "dsd-vps-kamal",
        reference_filename="deploy_sqlite.yml",
    )


def test_dockerfile_sqlite(tmp_project):
    """Dockerfile matches the default Kamal setup."""
    hf.check_reference_file(tmp_project, "Dockerfile", "dsd-vps-kamal")


def test_dockerignore_sqlite(tmp_project):
    hf.check_reference_file(
        tmp_project,
        ".dockerignore",
        "dsd-vps-kamal",
        reference_filename="dockerignore",
    )


def test_start_web_sh_sqlite(tmp_project):
    hf.check_reference_file(tmp_project, "start-web.sh", "dsd-vps-kamal")


def test_gitignore_sqlite(tmp_project):
    hf.check_reference_file(tmp_project, ".gitignore", "dsd-vps-kamal")
