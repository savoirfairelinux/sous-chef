from .settings import *


SECRET_KEY = "SecretKeyForUseOnTravis"

DEBUG = False
TEMPLATE_DEBUG = False

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
