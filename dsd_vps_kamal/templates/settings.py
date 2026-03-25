{{current_settings}}

# VPS Kamal settings.
import os

if os.environ.get("ON_VPS"):
{% if not use_sqlite %}    import dj_database_url
{% endif %}    from django.http import HttpResponse

    class HealthCheckMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            if request.path in ("/kamal/up", "/kamal/up/"):
                return HttpResponse("OK")
            return self.get_response(request)

    SECRET_KEY = os.environ.get("SECRET_KEY")

    if os.environ.get("DEBUG") == "FALSE":
        DEBUG = False
    elif os.environ.get("DEBUG") == "TRUE":
        DEBUG = True

    ALLOWED_HOSTS = ["{{ ip_address }}"{% if host %}, "{{ host }}"{% endif %}]

{% if use_sqlite %}    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/app/db/db.sqlite3",
            "OPTIONS": {
                "timeout": 20,
            },
        }
    }
{% else %}    db_url = os.environ.get("DATABASE_URL")
    DATABASES["default"] = dj_database_url.parse(db_url)
{% endif %}
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATIC_URL = "/static/"

    i = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(i, "{{settings_module_path}}.HealthCheckMiddleware")
    MIDDLEWARE.insert(i + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

    CSRF_TRUSTED_ORIGINS = ["https://{{ ip_address }}"{% if host %}, "https://{{ host }}"{% endif %}]
