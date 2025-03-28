"""
Django settings for dojo project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
CSRF_TRUSTED_ORIGINS = [
    'https://localhost',
    'https://127.0.0.1',
    'https://192.168.3.70',
    'https://*.ngrok-free.app',
]
# SESSION_COOKIE_SECURE = True   # Solo en producción con HTTPS
# CSRF_COOKIE_SECURE = True      # Solo en producción con HTTPS
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so'
# Close session when the browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Set session timeout to 30 minutes (1800 seconds)
SESSION_COOKIE_AGE = 1800


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user_management',
    'dashboard',
    'test'
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

ROOT_URLCONF = 'dojo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'dojo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    "default": {
        "ENGINE": os.environ.get("DOJO_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DOJO_DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DOJO_DB_USER", "user"),
        "PASSWORD": os.environ.get("DOJO_DB_PASS", "password"),
        "HOST": os.environ.get("DOJO_DB_HOST", "localhost"),
        "PORT": os.environ.get("DOJO_DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'user_management.User'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    "/app/static/",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------- LOGGING ---------------------------------------
logging_level = "DEBUG" if DEBUG else "INFO"
logging_path = BASE_DIR / "logs"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'formatters': {
        'main_formatter': {
            'format': '[%(asctime)s] {%(filename)s:%(lineno)d} '
                      '%(levelname)s:%(name)s %(message)s ',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(logging_path, 'main.log'),
            'when': 'D',
            'backupCount': 0,
            'formatter': 'main_formatter',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(logging_path, 'main_debug.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_true'],
        }
    },
    'loggers': {
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'debug_file'],
            'propagate': False,
        },
        'django': {
            'level': logging_level,
            'handlers': ['console', 'debug_file', 'production_file'],
        },
        'application': {
            'level': logging_level,
            'handlers': ['console', 'debug_file', 'production_file'],
        }
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
