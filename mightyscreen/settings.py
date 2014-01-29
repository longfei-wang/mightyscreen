"""
Django settings for mightyscreen project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n+&v$xnl)&ri&!#*z^a4jn%s6ms8n$o=ap%-&re+f^f5vn6ryo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapforms',
    'main',
    'south',
    'library',
    'djcelery',
    'kombu.transport.django',
    'data',
    'project',
    'statistics',
    'process',  
    #'mptt',
    #'compressor',
    'easy_thumbnails',
    #'fiber',
    'userenabootstrap',
    'userena',
    'guardian',
    'accounts',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'fiber.middleware.ObfuscateEmailAddressMiddleware',
    #'fiber.middleware.AdminPageMiddleware',
)

ROOT_URLCONF = 'mightyscreen.urls'

WSGI_APPLICATION = 'mightyscreen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'mightyscreen.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

TEMPLATE_CONTEXT_PROCESSORS=("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.core.context_processors.request",
"django.contrib.messages.context_processors.messages",
"django.core.context_processors.request")

MEDIA_ROOT =os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'


import djcelery
djcelery.setup_loader()
BROKER_URL="django://"

CELERY_TASK_SERIALIZER='json'

AUTH_PROFILE_MODULE = 'accounts.usersprofile'

# import django.conf.global_settings as DEFAULT_SETTINGS

# STATICFILES_FINDERS = DEFAULT_SETTINGS.STATICFILES_FINDERS + (
#     'compressor.finders.CompressorFinder',
# )


from mongoengine import connect

connect('mightyscreen')

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'yourgmailaccount@gmail.com'
EMAIL_HOST_PASSWORD = 'yourgmailpassword'

ANONYMOUS_USER_ID = -1
USERENA_WITHOUT_USERNAMES = True

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'


#read user agreement
f=open(BASE_DIR+'/README.md')
AGREEMENT=f.read()
f.close()