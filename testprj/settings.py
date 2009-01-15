DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '' # no database file is needed for running the test suite

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)

ROOT_URLCONF = 'deco.testprj.urls'

INSTALLED_APPS = (
    'deco',
     # we include the project package as an app so we can easily load the templates from it:
    'deco.testprj',
)

DECO_TESTPRJ = True
