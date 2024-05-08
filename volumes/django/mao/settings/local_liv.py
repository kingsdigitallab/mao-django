from .base import *  # noqa

ALLOWED_HOSTS = ['mao.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

# DATABASES = {
#     'default': {
#         'ENGINE': db_engine,
#         'NAME': 'app_mao_liv',
#         'USER': 'app_mao',
#         'PASSWORD': '',
#         'HOST': ''
#     },
# }

print("IN LIV ENVIRONMENT!!!")

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'mao',
        'USER': 'mao',
        'PASSWORD': 'mao',
        'HOST': 'postgres'
    },
}

SECRET_KEY = ''
