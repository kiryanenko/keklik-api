"""
Django settings for keklik project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('KEKLIK_API_SECRET_KEY', ')g9&5bdo3v-f*3rfyr8168zx9pxqp-d$4+6azac%qk1&pu#o3g')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('KEKLIK_API_DEBUG', True))

ALLOWED_HOSTS = [
    '127.0.0.1',
    '.keklik.xyz',
    'keklik-api.herokuapp.com',
    'keklik.herokuapp.com'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'channels',
    'channels_api',
    'corsheaders',
    'crispy_forms',
    'drf_yasg',
    'api',
    'organization'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'keklik.urls'

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

WSGI_APPLICATION = 'keklik.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'keklik'),
        'USER': os.environ.get('DATABASE_USER', 'keklik'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', '123456'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

AUTH_USER_MODEL = 'api.User'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'EXCEPTION_HANDLER': 'api.utils.errors.api_exception_handler',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


CORS_ORIGIN_WHITELIST = (
    'http://keklik.xyz',
    'http://cp.keklik.xyz',
    'https://keklik.herokuapp.com',
    'https://keklik-dev.herokuapp.com',
    'http://localhost',
    'http://localhost:3000',
    'http://176.57.208.231'
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = (
    'keklik.xyz',
    'api.keklik.xyz',
    'cp.keklik.xyz',
    'keklik-api.herokuapp.com',
    'keklik.herokuapp.com',
    'keklik-dev.herokuapp.com',
    'localhost',
    'localhost:3000',
    '176.119.156.90'
)


# Channels

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.core.RedisChannelLayer",
        "ROUTING": "keklik.routing.channel_routing",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# import logging
# log = logging.getLogger('django.db.backends')
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.StreamHandler())

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

if not DEBUG:
    django_heroku.settings(locals())
