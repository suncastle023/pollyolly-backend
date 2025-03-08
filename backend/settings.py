"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'accounts.CustomUser'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@c@o#s*3bg3o*ue^4cijk@-t(vtac*eb!gm%yg3n$f0(g24%)1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'pollyolly.store', 'www.pollyolly.store', '3.35.214.190']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'rest_framework',
    'corsheaders',
    'accounts',
    'users',
    'pet',
    'steps',
    'coin',
    'inventory',
    'store',
    'friend'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.kakao.KakaoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # 프로젝트의 템플릿 폴더 경로
        ],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'ko-kr'  # ✅ 한국어 설정
TIME_ZONE = 'Asia/Seoul'  # ✅ 한국 시간(KST)으로 변경

USE_I18N = True
USE_TZ = False  # ✅ 타임존 사용 비활성화 (데이터베이스에 저장될 시간을 한국 시간으로 직접 저장)



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from dotenv import load_dotenv

load_dotenv()

SOCIAL_AUTH_KAKAO_KEY = os.environ.get("SOCIAL_AUTH_KAKAO_KEY", "")
SOCIAL_AUTH_KAKAO_SECRET = os.environ.get("SOCIAL_AUTH_KAKAO_SECRET", "")
SOCIAL_AUTH_KAKAO_REDIRECT_URI = os.environ.get("SOCIAL_AUTH_KAKAO_REDIRECT_URI", "")


# ✅ CORS 설정 (모든 출처 허용 X, 명확한 출처 지정)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Flutter 웹앱 실행 주소
    "http://127.0.0.1:5173",
    "http://pollyolly.store", 
    "http://3.35.214.190",   
    "http://www.pollyolly.store",
]


CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False  # 쿠키를 JavaScript에서 접근할 수 있도록 설정
CSRF_COOKIE_SAMESITE = "Lax"  # CSRF 쿠키가 cross-site 요청에서 유효하게 설정
CSRF_COOKIE_SECURE = False  # HTTPS가 아니라면 False로 설정 (HTTPS라면 True)

SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
#SESSION_ENGINE = "django.contrib.sessions.backends.db"  # 기본 DB 세션 엔진
SESSION_COOKIE_SAMESITE = "Lax" 
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # Redis DB 1번 사용
    }
}


SESSION_COOKIE_AGE = 1209600  # 세션 유지 시간 (14일)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 브라우저 종료 시 세션 유지 여부
SESSION_SAVE_EVERY_REQUEST = True  # 사용자가 활동하면 세션 연장


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # ✅ JSONRenderer 사용
    ],
    'DEFAULT_CHARSET': 'utf-8',  # ✅ UTF-8 설정
}