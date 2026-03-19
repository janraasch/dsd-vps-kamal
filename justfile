# Default task
default:
    @just --list

# Run unit tests
test-unit:
    uv run pytest

# Run integration tests
test-integration:
    cd ../django-simple-deploy && uv run pytest && cd ../dsd-vps-kamal

# Run unit & integration tests
# Core picks up our unit tests automatically, so we don't need to run them here.
test: test-integration

# TODO: end-2-end tests

# Check linting (no fixes)
lint:
    uv run ruff format --check .
    uv run ruff check .

# Format code
format:
    uv run ruff format .
    uv run ruff check --fix .

# Set up CI environment (clone core + install deps)
ci-setup: dev-setup

# CI: lint + test
ci: lint test

# Set up development environment
dev-setup:
    #!/usr/bin/env bash
    set -euo pipefail
    # Clone django-simple-deploy if it doesn't exist
    if [ ! -d ../django-simple-deploy ]; then
        git clone https://github.com/django-simple-deploy/django-simple-deploy.git ../django-simple-deploy
    fi
    # Ensure venv exists in core, then install both packages in editable mode
    cd ../django-simple-deploy && uv venv --allow-existing && uv pip install -e ".[dev]" && uv pip install -e "../dsd-vps-kamal[dev]"

# TODO: Check what we need here
# Build package
# build:
#    uv run python -m build
#
# Upload to PyPI (test)
# publish-test:
#    uv run twine upload --repository testpypi dist/*
#
# Upload to PyPI
# publish:
#     uv run twine upload dist/*
#
# Clean build artifacts
# clean:
#   rm -rf dist/ build/ *.egg-info
