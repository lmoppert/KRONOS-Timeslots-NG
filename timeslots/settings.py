""" Django settings for timeslots project.

    Generated by 'django-admin startproject' using Django 2.0.1.

    For more information on this file, see
    https://docs.djangoproject.com/en/2.0/topics/settings/

    For the full list of settings and their values, see
    https://docs.djangoproject.com/en/2.0/ref/settings/
"""

from django.utils.translation import gettext_lazy as _
from timeslots.secrets import SECRET_KEY, PSQL_PASS
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

SECRET_KEY = SECRET_KEY
DEBUG = True
ALLOWED_HOSTS = [
    'kronos-timeslots.com',
    'timeslots.kronosww.com',
    'localhost',
    'testserver',
]
INTERNAL_IPS = ['127.0.0.1', '10.49.2.96']
ADMINS = [('Lutz Moppert', 'lutz.moppert@kronosww.com'), ]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'debug_toolbar',
    'widget_tweaks',
    'slots',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'timeslots.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'timeslots.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'new-timeslots',
        'HOST': 'localhost',
        'USER': 'timeslots',
        'PASSWORD': PSQL_PASS
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

UV = 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
AUTH_PASSWORD_VALIDATORS = [{
    'NAME': UV,
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}, ]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('de', _('German')),
    ('en', _('English'))
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


# Configure Plugins and Applications

SHELL_PLUS_PRE_IMPORTS = [('scripts.helper', 'generate_slots')]

ALERT_MESSAGES = [
    _('debug'),
    _('info'),
    _('success'),
    _('warning'),
    _('error'),
]

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': "",
    'SHOW_COLLAPSED': True,
}
