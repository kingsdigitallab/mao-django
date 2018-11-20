from .base import *  # noqa

ALLOWED_HOSTS = ['mao.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_mao_liv',
        'USER': 'app_mao',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''
