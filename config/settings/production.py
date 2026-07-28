from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# DATABASES
# ------------------------------------------------------------------------------
# DATABASES['default'] = env.db('DATABASE_URL')  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = False  # noqa F405

REDIS_URL = env.str("REDIS_URL")

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Session/CSRF cookies were being issued without the Secure attribute, so a
# browser would happily replay an admin session over plaintext. The deployment
# is HTTPS-only (Cloudflare terminates TLS, the origin only accepts Cloudflare
# IPs), so this is purely Django not being told.
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SESSION_COOKIE_HTTPONLY = env.bool("DJANGO_SESSION_COOKIE_HTTPONLY", default=True)

# TLS is terminated upstream, so request.is_secure() is False without this and
# Django treats every request as plaintext — which is also what makes the
# scheme-qualified entries in CSRF_TRUSTED_ORIGINS unreliable on the admin
# login POST. Trusting the header is safe only because the proxy sets it on
# every request; keep the escape hatch for anyone running this without one.
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
if env.bool("DJANGO_USE_X_FORWARDED_PROTO", default=True):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SSO (tested with https://github.com/buzzfeed/sso)
# ------------------------------------------------------------------------------
# Be really careful when enabling SSO. If the `SSO_USERNAME_HEADER` can be spoofed
# auth is broken and anyone will be able to log in as any user
SSO_ENABLED = env.bool("SSO_ENABLED", default=False)
if SSO_ENABLED:
    SSO_USERNAME_HEADER = env.str(
        "SSO_USERNAME_HEADER", default="HTTP_X_FORWARDED_USER"
    )
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    MIDDLEWARE.append(  # noqa F405
        "safe_transaction_service.utils.auth.CustomHeaderRemoteUserMiddleware"
    )
    AUTHENTICATION_BACKENDS = [
        "safe_transaction_service.utils.auth.CustomRemoteUserBackend"
        # "django.contrib.auth.backends.ModelBackend",
    ]
    # When creating a user, give superuser permissions if username is in SSO_ADMIN
    SSO_ADMINS = env.list("SSO_ADMINS", default=["richard", "uxio"])

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

# CELERY
# ------------------------------------------------------------------------------
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=REDIS_URL)

# Gunicorn
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["gunicorn"]  # noqa F405
