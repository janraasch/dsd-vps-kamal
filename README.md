# dsd-vps-kamal

🚧 **work in progress** 🚧

A [Django Simple Deploy][dsd-github-url] plugin for deploying [Django][django-url] projects to any VPS provider using [Kamal][kamal-url].

## Prerequisites

### Install [Kamal][kamal-url]

If you have a [Ruby][ruby-url] environment available, you can install [Kamal][kamal-url] using the following command:

```bash
gem install kamal
```

If you don't have a [Ruby][ruby-url] environment available, we recommend using [rv][rv-github-url] to install Kamal via

```bash
brew install rv # check https://github.com/spinel-coop/rv#installation for Windows instructions
rv tool install kamal # then you can run `kamal` using `rvx kamal`
```

### Setup a VPS with SSH access

Go to your VPS provider of choice (e.g. [Hetzner][hetzner-url], [Linode][linode-url], [DigitalOcean][digitalocean-url], etc.) and setup a VPS with SSH access, i.e. we want to be able to connect to your VPS using `ssh <your-vps-ip-address>`.

### (optional) Setup a DNS record for your VPS

If you want to use a custom domain name for your VPS, you can setup a DNS record for your VPS. This is optional, but recommended.

## Install the plugin

```bash
uv pip install dsd-vps-kamal
# Add "django_simple_deploy" to INSTALLED_APPS in settings.py.
git commit -am "Added django_simple_deploy to INSTALLED_APPS."
```

## Usage

```bash
python manage.py deploy
```

## Contributing

⚠️ `# TODO: Add contribution guidelines` ⚠️

[django-url]: https://www.djangoproject.com/
[dsd-github-url]: https://github.com/django-simple-deploy/django-simple-deploy
[kamal-url]: https://kamal-deploy.org/
[ruby-url]: https://www.ruby-lang.org/
[rv-github-url]: https://github.com/spinel-coop/rv
[rv-installation-url]: https://github.com/spinel-coop/rv#installation
[hetzner-url]: https://www.hetzner.com/
[linode-url]: https://www.linode.com/
[digitalocean-url]: https://www.digitalocean.com/
