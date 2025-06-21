# test_project/settings.py
SECRET_KEY = "dummy"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "tests",
    "tests.unit.apps.UnitTestsConfig",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
MIGRATION_MODULES = {
    "tests_unit": None,  # use label from UnitTestsConfig
}
