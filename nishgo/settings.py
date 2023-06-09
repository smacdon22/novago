"""
Django settings for nishgo project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import dj_database_url
import os
from pathlib import Path
from django.test.runner import DiscoverRunner

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

IS_HEROKU = "DYNO" in os.environ

[print(IS_HEROKU) for i in range(10)]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'v^!m58!_$suhcrjr&!cjxj=#fss)8plr378w4%j(dkm%*@3s^b'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51MgrsGBQaa9YVByTDOqfwq6KRbSHLpXz7qlbHfrEYZ6GlCTAcCOfS3twyzLtorKVOfF7pJ6sWihyDApoy8Z9iUww00PxffUbrG'
STRIPE_SECRET_KEY = 'sk_test_51MgrsGBQaa9YVByTibBRyP0pJe900jB034J6VUV05ZsHUnOzz31E4WQV3eRGQNPo0avPD4T5x1AsYtGsrYvlzlpp0058XVXTOl'


try:
    # get secret key from env
    if 'SECRET_KEY' in os.environ:
        SECRET_KEY = os.environ["SECRET_KEY"]
    # get api key from env
    if 'API_KEY' in os.environ:
        API_KEY = os.environ["API_KEY"]
    # get auth0 domain from env
    if 'AUTH0_DOMAIN' in os.environ:
        AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
    # get auth0 client id from env
    if 'AUTH0_CLIENT_ID' in os.environ:
        AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
    # get auth0 client secret from env
    if 'AUTH0_CLIENT_SECRET' in os.environ:
        AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
    # get stripe publishable key from env
    if 'STRIPE_PUBLISHABLE_KEY' in os.environ:
        STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]
    # get stripe secret key from env
    if 'STRIPE_SECRET_KEY' in os.environ:
        STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
    # get gmap secret key from env
    if 'GMAPS_CLIENT_KEY' in os.environ:
        GMAPS_CLIENT_KEY = os.environ["GMAPS_CLIENT_KEY"]
except KeyError as e:
    print(f"Environment variable {e} is missing.")


# secret key found on heroku: v^!m58!_$suhcrjr&!cjxj=#fss)8plr378w4%j(dkm%*@3s^b
# replaced with gfg%tf47xorp9^4#^7ouw8srzfw(b2et)tid05mth45lyh#e1&
# if 'SECRET_KEY' in os.environ:
#     SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
if not IS_HEROKU:
    DEBUG = True

# Generally avoid wildcards(*). However since Heroku router provides hostname validation it is ok
if IS_HEROKU:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'novago.apps.novagoConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nishgo.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, "novago", 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR,],
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

WSGI_APPLICATION = 'nishgo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL']
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'novago/static'
STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

API_KEY = os.environ.get('API_KEY')
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
GMAPS_CLIENT_KEY = os.environ.get("GMAPS_CLIENT_KEY")

# django_on_heroku.settings(locals())
