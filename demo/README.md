# django-siteforms demo

<http://github.com/idlesign/django-siteforms>

This Django project demonstrates siteforms basic features.

Expects Python 3.10+ and Django 5.2+.

The project uses [uv](https://docs.astral.sh/uv/) for dependency management
and installs django-siteforms from the local sources (repository root),
so package changes are visible right away.

## How to run

### Docker

1.  Run `docker compose up`
2.  Go to <http://localhost:8000>

### Manually

1.  Install the dependencies with `uv sync`
2.  Run the server `uv run python manage.py runserver`
3.  Go to <http://localhost:8000>

### Admin

Admin (<http://localhost:8000>) credentials:

- Login: `demo`
- Password: `demodemo`
