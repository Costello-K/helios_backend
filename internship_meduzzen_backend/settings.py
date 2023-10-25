import os
from datetime import timedelta
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', default=False)

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'djoser',
    'social_django',
    'corsheaders',
    'drf_yasg',

    'api_v1',
    'user',
    'company',
    'quiz',
    'message',

    'common',
    'tests',
]

MIDDLEWARE = [
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'internship_meduzzen_backend.urls'

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

WSGI_APPLICATION = 'internship_meduzzen_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PSQL_NAME'),
        'USER': os.environ.get('PSQL_USER'),
        'PASSWORD': os.environ.get('PSQL_PASSWORD'),
        'HOST': os.environ.get('PSQL_HOST'),
        'PORT': os.environ.get('PSQL_PORT'),
    }
}

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = os.environ.get('REDIS_DB')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS_DATA_EXPIRATION = 60 * 60 * 48

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('uk', _('Ukraine')),
)

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Extra places for collect static files.

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
DEFAULT_USER_AVATAR_URL = os.path.join(MEDIA_URL, 'default/images/users/avatar.png')
USER_AVATAR_MAX_SIZE_MB = 2


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# User
AUTH_USER_MODEL = "user.CustomUser"

# AUTH

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.SettingsPageNumberPagination',
}


# DJOSER
DJOSER = {
    'SERIALIZERS': {
        'user': 'user.serializers.UserSerializer',
        'current_user': 'user.serializers.UserSerializer',
        'user_create': 'user.serializers.UserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.IsAuthenticated'],
        'user_create': ['rest_framework.permissions.AllowAny'],
    },
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': [
        f'http://{ALLOWED_HOSTS[0]}/authorization'
    ],
    'TOKEN_MODEL': None,
    'LOGIN_FIELD': 'username',
    'SEND_ACTIVATION_EMAIL': True,
    'EMAIL': {
        'activation': 'internship_meduzzen_backend.email.ActivationEmail',
        'password_reset': 'internship_meduzzen_backend.email.PasswordResetEmail',
        'username_reset': 'internship_meduzzen_backend.email.UsernameResetEmail',
    },
    'ACTIVATION_URL': 'auth/users/activate/{uid}/{token}',
    'PASSWORD_RESET_CONFIRM_URL': 'auth/users/reset_confirm/password/{uid}/{token}',
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'USERNAME_RESET_CONFIRM_URL': 'auth/users/reset_confirm/username/{uid}/{token}/',
    'USERNAME_RESET_SHOW_EMAIL_NOT_FOUND': True,
}

# DJOSER JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer', ),
}

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# Google OAuth 2.0 settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [
    'first_name',
    'last_name',
]
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
]

# Facebook OAuth 2.0 settings
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    'public_profile',
]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'email, name',
}


# LOGGING
# Path to the log folder
log_dir = os.path.join(BASE_DIR, 'logs')

# Create a folder for logs if it does not exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%{asctime:25s}{filename:25s}{lineno:3d} {levelname:8s}{message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'event_log.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8081',
    'http://localhost:8081',
]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Quiz settings
MIN_COUNT_QUESTIONS = 2
MIN_COUNT_ANSWERS = 2
