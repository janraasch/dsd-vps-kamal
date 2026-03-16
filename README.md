# dsd-vps-kamal [![lint](https://github.com/janraasch/dsd-vps-kamal/actions/workflows/lint.yaml/badge.svg)](https://github.com/janraasch/dsd-vps-kamal/actions/workflows/lint.yaml) [![tests](https://github.com/janraasch/dsd-vps-kamal/actions/workflows/integration_tests.yaml/badge.svg)](https://github.com/janraasch/dsd-vps-kamal/actions/workflows/integration_tests.yaml)

A [django-simple-deploy][dsd-url] plugin for deploying [Django][django-url] projects to any VPS using [Kamal][kamal-url].

[Hetzner][hetzner-url], [DigitalOcean][digitalocean-url], [Linode][linode-url] et al. — if you can SSH into it, you can deploy to it.

- [Current Status 🙋‍♂️](#current-status-️)
- [Installation 💻](#installation-)
- [Configuration-only mode](#configuration-only-mode)
- [Fully automated deployment ⚡](#fully-automated-deployment-)
- [Options](#options)
    - [`--ip-address` (required)](#--ip-address-required)
    - [`--host` (required for HTTPS, optional otherwise)](#--host-required-for-https-optional-otherwise)
    - [`--sqlite` (optional)](#--sqlite-optional)
- [Installing Kamal 🔧](#installing-kamal-)
- [Development 🛠️](#development-️)
- [Special Thanks ❤️](#special-thanks-)
- [License 📄](#license-)

## Current Status 🙋‍♂️

This plugin is in a **pre-1.0 development phase**. It's ready for use, but the API is not yet stable. See the [roadmap to v1][v1-issue-url] for what's planned.

## Installation 💻

```shell
pip install dsd-vps-kamal
```

Then add `django_simple_deploy` to `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_simple_deploy",
]
```

## Usage 🧑‍🔧

### Configuration-only mode

By default, the plugin configures your project for deployment but doesn't actually deploy. You review the changes, commit, and deploy yourself:

```shell
python manage.py deploy --ip-address <your-vps-ip>
```

This generates all the files [Kamal][kamal-url] needs — `deploy.yml`, `Dockerfile`, secrets, and production settings. Review the changes, then:

```shell
git add .
git commit -m "Configured for deployment via Kamal."
rvx kamal setup # see »Installing Kamal« below for more details
```

### Fully automated deployment ⚡

Pass `--automate-all` and the plugin handles everything — configuration, committing, and running `kamal setup` for you:

```shell
python manage.py deploy --automate-all --ip-address <your-vps-ip>
```

This requires a few things to be in place:

- **VPS provisioning is out of scope (for now)** — bring your own server; this command does not create or configure the VPS itself yet.
- **SSH root access** — `ssh root@<your-vps-ip>` must work without a password prompt
- **Docker running locally** — the [Docker daemon needs to be active](https://docs.docker.com/get-started/overview/#docker-desktop) on your machine. We recommend [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Kamal installed locally** — see [Installing Kamal](#installing-kamal-) below

### Options

#### `--ip-address` (required)

The IPv4 address of your VPS. This is how the plugin knows where to deploy.

#### `--host` (required for HTTPS, optional otherwise)

A domain name for [Kamal][kamal-url]'s proxy routing, e.g. `myapp.example.com`. If you've pointed a DNS record at your VPS, pass it here:

```shell
python manage.py deploy --ip-address <your-vps-ip> --host myapp.example.com
```

If omitted, your app is served over HTTP on the IP address (no automatic TLS certificate).

#### `--sqlite` (optional)

Use SQLite instead of PostgreSQL:

```shell
python manage.py deploy --ip-address <your-vps-ip> --sqlite
```

Uses [dj-lite][dj-lite-url] for production-ready SQLite by default.

## Installing Kamal 🔧

[Kamal][kamal-url] is a Ruby gem. If you already have Ruby set up:

```shell
gem install kamal
```

If you'd rather not manage a Ruby environment, we recommend [rv][rv-url]:

```shell
brew install rv  # see https://github.com/spinel-coop/rv#installation for other OSes
rv tool install kamal
```

Then use `rvx kamal` wherever you'd normally run `kamal`. The plugin detects `rv` automatically when using `--automate-all`.

## Development 🛠️

Install [Just](https://github.com/casey/just) to run the development commands:

```shell
just dev-setup  # clones core + installs everything in editable mode
```

```
## Other `just` recipes for development:
    lint             # Check linting (no fixes)
    format           # Format code
    test-unit        # Run unit tests
    test-integration # Run integration tests
```

All available `just` commands:

```
just --list
```

## Special Thanks ❤️

- **Eric Matthes** for [django-simple-deploy][dsd-url] — making Django deployment accessible to everyone
- **David Heinemeier Hansson** for [Kamal][kamal-url] — zero-downtime deployments to any VPS without the complexity
- **Jeff Triplett** for [django-startproject][django-startproject-url] — a fantastic project template and inspiration
- **Adam Hill** for [dj-lite][dj-lite-url] — production-ready SQLite for Django
- The **[Djangonauts][djangonauts-url]** program & **Team Venus** 🪐 - [Session 6](https://djangonaut.space/comms/2026/02/19/session-6-team-introductions/)

## License 📄

[BSD 3-Clause](LICENSE) © [Jan Raasch][author-url]

[django-url]: https://www.djangoproject.com/
[dsd-url]: https://github.com/django-simple-deploy/django-simple-deploy
[kamal-url]: https://kamal-deploy.org/
[rv-url]: https://github.com/spinel-coop/rv
[hetzner-url]: https://www.hetzner.com/
[digitalocean-url]: https://www.digitalocean.com/
[linode-url]: https://www.linode.com/
[dj-lite-url]: https://github.com/adamghill/dj-lite
[django-startproject-url]: https://github.com/jefftriplett/django-startproject
[djangonauts-url]: https://djangonaut.space
[author-url]: https://www.janraasch.com
[v1-issue-url]: https://github.com/janraasch/dsd-vps-kamal/issues/3
