# Default task
default:
    @just --list

# Run unit tests
test-unit:
    uv run pytest

# Run integration tests
test-integration:
    cd ../django-simple-deploy && uv run pytest && cd ../dsd-vps-kamal

# TODO: end-2-end tests

# Check linting (no fixes)
lint:
    uv run ruff format --check .
    uv run ruff check .

# Format code
format:
    uv run ruff format .
    uv run ruff check --fix .

# CI: lint + test
ci: lint test-unit test-integration

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
