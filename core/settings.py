"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import secrets

import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENV = environ.Env()

PROJECT_NAME = str(ENV.get_value('BF_PROJECT_NAME', default='bros files'))
_PROJECT_NAME = ''.join(PROJECT_NAME.split())

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.get_value('BF_SECRET_KEY')
BF_JWT_AUTH_KEY = ENV.get_value('BF_JWT_AUTH_KEY')

# By default, always run in production mode
DEBUG = ENV.get_value('BF_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ENV.get_value('BF_ALLOWED_HOSTS', cast=list)

if DEBUG is False:
    SECURE_SSL_REDIRECT = True

    if ENV.get_value('BF_CSRF_TRUSTED_ORIGINS', default=None) is None:
        CSRF_TRUSTED_ORIGINS = ['https://%s' % _host for _host in ALLOWED_HOSTS]
    else:
        CSRF_TRUSTED_ORIGINS = ENV.get_value('BF_CSRF_TRUSTED_ORIGINS', cast=list)

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        )
    }

##################
# AUTHENTICATION #
##################
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = "/accounts/signin/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = None


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party apps
    'fontawesomefree',
    # Custom apps
    'accounts',
    'base',
    'docs',
    'payments',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

if ENV.get_value('BF_PSQL_PASSWORD', default=None) is None:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': ENV.get_value('BF_PSQL_NAME', default=_PROJECT_NAME),
            'USER': ENV.get_value('BF_PSQL_USER', default=_PROJECT_NAME),
            'PASSWORD': ENV.get_value('BF_PSQL_PASSWORD'),
            'HOST': ENV.get_value('BF_PSQL_HOST'),
            'PORT': ENV.get_value('BF_PSQL_PORT', default='5432'),
        },
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

########
# CSRF #
########

CSRF_FAILURE_VIEW = "base.views.csrf_failure"

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

AWS_STORAGE_BUCKET_NAME = ENV.get_value('AWS_STORAGE_BUCKET_NAME', default=None)

if AWS_STORAGE_BUCKET_NAME is not None:
    AWS_ACCESS_KEY_ID = ENV.get_value('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = ENV.get_value('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = ENV.get_value('AWS_S3_REGION_NAME')

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    BF_CLOUD_STORAGE_SITE = ENV.get_value('BF_CLOUD_STORAGE_SITE', default=None)

    if BF_CLOUD_STORAGE_SITE is not None:
        AWS_S3_ENDPOINT_URL = 'https://s3.%s.%s' % (AWS_S3_REGION_NAME, BF_CLOUD_STORAGE_SITE)

    STATIC_URL = '/static/'
    STATIC_ROOT = str(BASE_DIR / 'static/')
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = str(BASE_DIR / 'static/')

    MEDIA_URL = '/media/'
    MEDIA_ROOT = str(BASE_DIR / 'media/')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# [CEO]
PROJECT_BUILD_HASH = secrets.token_hex(nbytes=16)
PROJECT_TITLE = ''.join(_i.capitalize() for _i in PROJECT_NAME.split())
PROJECT_DESCRIPTION = '%s is a free file storage' % PROJECT_TITLE
PROJECT_URL = ''
PROJECT_KEYWORDS = 'free, files, storage'

if DEBUG:
    PROJECT_ROBOTS = 'none, noarchive'
else:
    PROJECT_ROBOTS = 'index'
# [/CEO]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = ENV.get_value('DEFAULT_FROM_EMAIL')

EMAIL_HOST_USER = ENV.get_value('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = ENV.get_value('EMAIL_HOST_PASSWORD')

EMAIL_HOST = ENV.get_value('EMAIL_HOST')

EMAIL_PORT = ENV.get_value('EMAIL_PORT', cast=int, default=587)

EMAIL_USE_TLS = True

# Payments
PAYMENT_HOST = ENV.get_value('BF_PAYMENT_HOST')

PAYMENT_USES_SSL = DEBUG

STRIPE_PUBLIC_KEY = ENV.get_value('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = ENV.get_value('STRIPE_SECRET_KEY')
STRIPE_ENDPOINT_SECRET = ENV.get_value('STRIPE_ENDPOINT_SECRET')
