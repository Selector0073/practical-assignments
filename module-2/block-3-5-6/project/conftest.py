"""
Shared pytest fixtures for the unified DRF project.

Replaces Flask's application-factory / fixture pattern with pytest-django:

* ``test_db``  (session)  — forces the test database to PostgreSQL
   (``library_test_db``) matching the original Dockerised test setup. If a
   PostgreSQL server is not reachable it falls back to SQLite so the suite can
   run anywhere. pytest-django's own ``django_db_setup``/``--create-db``
   machinery handles creation.
* ``client``   (function) — a DRF ``APIClient``.

Each test that touches the DB is wrapped in ``pytest.mark.django_db``; Django's
transaction rollback replaces the manual ``TRUNCATE ... RESTART IDENTITY
CASCADE`` cleanup from the Flask original (a clean slate before every test).
"""
import os
import django
import pytest

from django.conf import settings as django_settings


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()


def _postgres_config_from_url(url):
    url = url.replace('postgres://', '').replace('postgresql://', '')
    userpass, _, rest = url.partition('@')
    user, _, password = userpass.partition(':')
    hostport, _, dbname = rest.rpartition('/')
    host, _, port = hostport.partition(':')
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': dbname or 'library',
        'USER': user or 'postgres',
        'PASSWORD': password or 'postgres',
        'HOST': host or '127.0.0.1',
        'PORT': port or '5432',
        'ATOMIC_REQUESTS': False,
    }


def _postgres_reachable(cfg):
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=cfg['HOST'], port=cfg['PORT'],
            user=cfg['USER'], password=cfg['PASSWORD'], dbname=cfg['NAME'],
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope='session', autouse=True)
def test_db():
    """(session) — point the test database at PostgreSQL ``library_test_db``,
    falling back to in-memory SQLite when Postgres is unavailable."""
    pg_cfg = None

    test_url = os.environ.get('TEST_DATABASE_URL')
    if test_url:
        pg_cfg = _postgres_config_from_url(test_url)
    else:
        # Match the Docker command in the README (postgres:17 on :5432).
        pg_cfg = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'library',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }

    if _postgres_reachable(pg_cfg):
        pg_cfg['TEST'] = {'NAME': 'library_test_db'}
        # Merge into the existing default so Django's other DB keys (if any)
        # are preserved, then apply.
        merged = dict(django_settings.DATABASES['default'])
        merged.update(pg_cfg)
        merged['ATOMIC_REQUESTS'] = False
        django_settings.DATABASES['default'] = merged
    else:
        merged = dict(django_settings.DATABASES['default'])
        merged.update({
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'ATOMIC_REQUESTS': False,
        })
        django_settings.DATABASES['default'] = merged

    return django_settings.DATABASES


@pytest.fixture
def client():
    """(function) — DRF APIClient used by every library test."""
    from rest_framework.test import APIClient
    return APIClient()
