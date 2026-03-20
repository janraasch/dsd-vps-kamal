{{current_settings}}

# VPS Kamal settings.
import os

if os.environ.get("ON_VPS"):
    import dj_database_url

    SECRET_KEY = os.environ.get("SECRET_KEY")

    if os.environ.get("DEBUG") == "FALSE":
        DEBUG = False
    elif os.environ.get("DEBUG") == "TRUE":
        DEBUG = True

    ALLOWED_HOSTS = ["{{ ip_address }}"{% if host %}, "{{ host }}"{% endif %}]

    db_url = os.environ.get("DATABASE_URL")
    DATABASES["default"] = dj_database_url.parse(db_url)

    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATIC_URL = "/static/"

    i = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(i + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

    CSRF_TRUSTED_ORIGINS = ["https://{{ ip_address }}"{% if host %}, "https://{{ host }}"{% endif %}]
