from pathlib import Path
import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
import pyrebase
import firebase_admin
from firebase_admin import credentials

# Carregar variáveis do arquivo .env
load_dotenv()

# Caminho para o diretório base
BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança: Chave secreta (não deixe visível em produção)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
FIREBASE_MEASUREMENT_ID = os.getenv('FIREBASE_MEASUREMENT_ID')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')

# Verificar se a chave secreta foi carregada corretamente
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")

# Debug mode - em produção, deve ser False
DEBUG = True

# Permitir apenas acesso local ou seu domínio específico
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'your-domain.com']

# Instalação dos aplicativos
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'gestor',
    'professor',
    'salas',
    'materiais',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL padrão
ROOT_URLCONF = 'sistema.urls'

# Configuração das templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# WSGI Application
WSGI_APPLICATION = 'sistema.wsgi.application'

# Banco de dados SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuração de senhas
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

# Localização do arquivo de configuração
LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos (CSS, JS, Imagens)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Adicionado para corrigir erro no deploy

# Arquivos de mídia (uploads de arquivos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Tipo de campo auto gerado para a chave primária
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de segurança para produção (opcional)
CSRF_COOKIE_SECURE = True  # Apenas se usar HTTPS
SESSION_COOKIE_SECURE = True  # Apenas se usar HTTPS

# Caminho para o arquivo JSON da chave privada do Firebase
FIREBASE_ADMIN_CREDENTIAL = os.path.join(BASE_DIR, 'sistemamapeamentolaboratorio-firebase-adminsdk-dmdt8-8bb2f08483.json')


# Inicializando o Firebase com a chave privada
cred = credentials.Certificate(FIREBASE_ADMIN_CREDENTIAL)
firebase_admin.initialize_app(cred)

# Configurações de Firebase (carregadas do .env)
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')

# Exemplo de como configurar Firebase (com pyrebase)
firebase_config = {
    "apiKey": FIREBASE_API_KEY,
    "authDomain": FIREBASE_AUTH_DOMAIN,
    "databaseURL": FIREBASE_DATABASE_URL,
    "projectId": FIREBASE_PROJECT_ID,
    "storageBucket": FIREBASE_STORAGE_BUCKET,
    "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
    "appId": FIREBASE_APP_ID,
}

# Inicializando o Firebase com a configuração do Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
database = firebase.database()
