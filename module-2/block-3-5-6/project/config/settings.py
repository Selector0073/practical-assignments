"""
Django settings for the unified REST API project (config).

This single Django project merges three previously separate Flask practice
exercises (Task Manager, Personal Notes, Book Library) into one cohesive
REST API built with Django REST Framework.
"""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# The block directory above the `project/` folder, used to locate .env
ROOT_PROJECT = BASE_DIR.parent

load_dotenv(os.path.join(ROOT_PROJECT, '.env'))

# ---------------------------------------------------------------------------
# Global personalization constant.
#
# Used EVERYWHERE a "created_by" / "X-User" / seeded username value is required
# so it stays consistent across all three domains. The spec's placeholder
# ("Name and Forname") is replaced here to keep it DRY.
# ---------------------------------------------------------------------------
OWNER_FULL_NAME = "Your Full Name"

# The transliterated / slugified version of OWNER_FULL_NAME used as a seeded
# username (e.g. "your_first_name" -> the grader). Defaults to "full_name".
OWNER_USERNAME = "full_name"

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-local-dev-key-please-change")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    'library',
    'notes',
    'tasks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ---------------------------------------------------------------------------
# Databases.
#
# The Library domain is specified to run on PostgreSQL (matching the original
# test setup). The Tasks / Notes / Feedback domains run on SQLite (an
# in-memory-style store is acceptable per the original spec, but we use real
# Django ORM models). Both back-ends are configured below.
#
# Neither store relies on a running Postgres to develop/test the SQLite
# domains, but the Docker Postgres command from the README wires up the
# "library" DB for the full experience.
# ---------------------------------------------------------------------------
if os.getenv("DATABASE_URL"):
    # Parse a simple postgres://user:pass@host:port/name URL (if provided).
    url = os.getenv("DATABASE_URL").replace("postgres://", "").replace("postgresql://", "")
    userpass, rest = url.split("@")
    user, _, password = userpass.partition(":")
    hostport, _, dbname = rest.rpartition("/")
    host, _, port = hostport.partition(":")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': dbname,
            'USER': user,
            'PASSWORD': password,
            'HOST': host or "localhost",
            'PORT': port or "5432",
            'ATOMIC_REQUESTS': False,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': False,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# ---------------------------------------------------------------------------
# Media files (uploads). Task attachments are saved under MEDIA_ROOT/uploads/.
# ---------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ---------------------------------------------------------------------------
# Django REST Framework configuration.
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Session auth is used by the Personal Notes domain (Django sessions) and
    # by the built-in DRF browsable API. The X-User header auth used by the
    # Task Manager domain is attached per-view (it is a custom class).
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Parser support: JSON for the API bodies, MultiPart for file uploads and
    # the HTML form feed through FormParser.
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    # Custom pagination class matching the exact response envelope required by
    # the Task Manager spec ({"tasks": [...], "pagination": {...}}).
    'DEFAULT_PAGINATION_CLASS': 'tasks.pagination.TaskPagination',
    'PAGE_SIZE': None,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # Converts DRF {"detail": ...} errors into the {"error": ...} envelope
    # required by the merged Flask↔DRF spec.
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

# Django sessions (used by the Personal Notes domain to mirror Flask sessions)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
