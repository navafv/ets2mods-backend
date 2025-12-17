from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# Security Settings
# ==========================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Parse allowed hosts and remove whitespace
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', cast=Csv())]

# ==========================================
# Application Definition
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', 
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'drf_yasg',
    'mptt',  # Needed for forums

    # Local Apps
    'users.apps.UsersConfig',
    'categories.apps.CategoriesConfig',
    'mods.apps.ModsConfig',
    'reviews.apps.ReviewsConfig',
    'forums.apps.ForumsConfig',
    'analytics.apps.AnalyticsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ==========================================
# Database
# ==========================================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG  # Enforce SSL in production
    )
}

# ==========================================
# Password Validation
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================
# Internationalization
# ==========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==========================================
# Static & Media Files
# ==========================================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cloudinary Storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==========================================
# Auth & Rest Framework
# ==========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User' 

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_RATES': {
        'uploads': '10/day',
        'downloads': '1000/day', # Increased for usability
        'user': '1000/day',
        'anon': '100/day',
    },
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'uploads': '10/day',
        'downloads': '100/day',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # Longer refresh for better UX
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# ==========================================
# CORS & CSRF
# ==========================================
# Clean whitespace from list items
CORS_ALLOWED_ORIGINS = [o.strip() for o in config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='http://localhost:5173')]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default='http://localhost:5173')]

# ==========================================
# AllAuth Settings
# ==========================================
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = 'none' 
ACCOUNT_AUTHENTICATION_METHOD = 'username' 
ACCOUNT_EMAIL_REQUIRED = True

# ==========================================
# Email & Frontend
# ==========================================
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@ets2mods.com')
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# ==========================================
# Production Security Headers
# ==========================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True