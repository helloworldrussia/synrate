from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-knlrtz6ws_wbw_%$uo0wrozvbzk!h5vy6c76k9l3dee(n#nx%2'
SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['127.0.0.1', 'synrate.ru', 'www.synrate.ru']
ALLOWED_HOSTS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'synrate',
    'Users',
    'synrate_main',
    'rest_framework',


    'parsers',

    'cms',

    'menus',
    'treebeard',
    'sekizai',
    'easy_thumbnails',
    'mptt',

    'filer',
    'djangocms_text_ckeditor',
    'djangocms_link',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_video',
    'djangocms_googlemap',
    'djangocms_snippet',
    'djangocms_style',



]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'

]

ROOT_URLCONF = 'synrate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
            ],
            'libraries' : {
                            'staticfiles': 'django.templatetags.static',
            }
        },
    },
]
CMS_TEMPLATES = [
    ('home.html', 'sample template'),
    ('base.html', 'base template'),
    ('user_base.html', 'user base template'),
    ('favorites.html', 'user favorites template'),
    ('cabinet.html', 'user cabinet template'),
    ('test.html', 'test template'),
    ('faq.html', 'FAQ template'),
    ('awaiting.html', 'closed template'),
    ('registr.html', 'registration template'),
    ('main.html', 'intro template')
]
CMS_PERMISSION = True
CMS_PLACEHOLDER_CONF = {}

WSGI_APPLICATION = 'synrate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'synrate_db',
        'USER': 'synrate',
        'PASSWORD': '0M3p8M1e',
        'HOST': '91.221.70.92',
        'PORT': '5432'
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
AUTH_USER_MODEL = 'Users.SynrateUser'
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Russian'),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    # '/var/www/static/',
]


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'



# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'SAMEORIGIN'

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

