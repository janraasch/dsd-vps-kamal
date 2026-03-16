# dsd-vps-kamal

Plugin for [django-simple-deploy](https://github.com/ehmatthes/django-simple-deploy) that deploys Django projects to any VPS using Kamal. Pre-1.0 beta.

## Architecture

- Core library (`django-simple-deploy`) exposes `dsd_config` (project settings), `plugin_utils` (file ops, template rendering), `DSDCommandError`
- Plugin hooks registered via pluggy: `dsd_deploy`, `dsd_get_plugin_config`, `dsd_get_plugin_cli`, `dsd_validate_cli`
- Plugin config shared with core via `plugin_config` singleton (`PluginConfig` class)
- Templates use Django's template engine, rendered via `plugin_utils.get_template_string()`
- Files written to user's project via `plugin_utils.add_file(path, contents)`
- `plugin_utils.remove_doubled_blank_lines()` is available after template rendering, but only use it if the template actually produces doubled blank lines (e.g. from conditional blocks)

## Plugin file map

- `__init__.py` — hook registration entry point
- `cli.py` — CLI args (`--ip-address`, `--host`, `--sqlite`) and validation
- `plugin_config.py` — `PluginConfig` singleton with `ip_address`, `host`, `use_sqlite`, `kamal_cmd`
- `platform_deployer.py` — core deployment logic (validation, file generation, automate-all flow)
- `deploy.py` — hook implementations connecting to core
- `deploy_messages.py` — user-facing messages and instructions
- `templates/` — `deploy.yml`, `dockerfile`, `dockerignore`, `kamal_secrets`, `settings.py`, `start-web.sh`

## Templates

- PostgreSQL vs SQLite conditional branching throughout (deploy.yml, kamal_secrets, settings.py)
- `mark_safe()` required for generated secrets — Django template engine auto-escapes by default
- Placeholder convention: `__DOUBLE_UNDERSCORES__` (not `<>` or `{}` which conflict with HTML escaping / Django templates)
- deploy.yml needs EOF normalization (trailing newline consistency)

## Implementation details

- Kamal CLI detection: tries `kamal version`, falls back to `rvx kamal`
- SSH checks use `-o BatchMode=yes -o ConnectTimeout=5`
- Automate-all flow: commits changes, runs `kamal setup`, opens browser

## Testing

- **Unit tests**: `tests/unit_tests/` — run with `just test-unit` (pytest + pytest-mock, monkeypatch + mocker)
- **Integration tests**: `tests/integration_tests/` — run with `just test-integration` (runs from core's directory)
  - Compare generated files against `reference_files/` using `filecmp.cmp` (exact match including trailing whitespace/newlines)
  - Updating templates means updating reference files too
  - Fixtures (`tmp_project`, `run_dsd`, etc.) come from core's `tests/integration_tests/conftest.py`
- **E2E tests**: `just test-e2e` / `just test-e2e-sqlite` — live deployment to Hetzner servers, requires hcloud CLI + active Hetzner context
- `dsd_config.unit_testing` is True during test runs; use it to skip real-world checks (SSH, API calls)
- dsd-pythonanywhere is the best reference for unit test patterns

## Dev setup

- `just dev-setup` — clones `django-simple-deploy` core as a sibling directory (`../django-simple-deploy/`) if not already present, then installs both core and this plugin in editable mode into core's venv
- Integration and e2e tests run from core's directory (`../django-simple-deploy/`), so core must be cloned as a sibling
- Other plugins are useful as reference implementations but are not cloned by dev-setup:
  - [dsd-pythonanywhere](https://github.com/caktus/dsd-pythonanywhere) — best reference for unit test patterns
  - [dsd-scalingo](https://github.com/ehmatthes/dsd-scalingo) — recent plugin by the core maintainer, good reference for SSH and general patterns
  - [dsd-flyio](https://github.com/django-simple-deploy/dsd-flyio) — good reference for templates/config
  - [dsd-vps](https://github.com/django-simple-deploy/dsd-vps) — good reference for SSH/CLI args

## Dev commands

- `just test-unit` / `just test-integration` / `just test` / `just test-e2e` / `just test-e2e-sqlite`
- `just lint` — ruff format check + ruff check
- `just format` — ruff format + ruff check --fix
- `just ci` — lint + tests

## Code quality

- Ruff configured in `pyproject.toml` (line-length 120, target py313, rules: E, F, UP, B, SIM, I)
- Always run `just lint` and `just format` before committing

## Conventions

- Always use TDD: write failing test first, watch it fail, then write minimal code to pass
- Follow existing plugin patterns (dsd-flyio for templates/config, dsd-pythonanywhere for unit tests, dsd-vps for SSH/CLI args)
- Placeholder values in templates use `__DOUBLE_UNDERSCORES__` convention

## Keeping this file up to date

If you notice something in this CLAUDE.md is out of date, or you learn something during work that would be useful to remember (e.g. a non-obvious pattern, a gotcha, a new convention), prompt the user to update this file.
