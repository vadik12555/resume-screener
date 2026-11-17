import tempfile

from .settings import *  # noqa: F401,F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CELERY_TASK_ALWAYS_EAGER = True
MEDIA_ROOT = tempfile.mkdtemp()
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
