import json
import os
from datetime import timedelta

from appdirs import AppDirs

APP_NAME = "Algo Trader"      
#app_dirs = AppDirs(APP_NAME)
#APP_CACHE_FOLDER = app_dirs.user_cache_dir
#APP_DATA_FOLDER = app_dirs.user_data_dir

#PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
#TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'backend', 'templates')
#STATIC_FOLDER = os.environ.get('FLASK_STATIC_FOLDER',os.path.join(PROJECT_ROOT, 'static'))
#STATIC_URL_PATH = '/static'  # serve asset files in static/ at /static/



def get_server_config():
    with open('../config/server.json', 'r') as server:
      json_server_data = json.load(server)
      return json_server_data


def get_system_config():
    with open('../config/system.json', 'r') as system:
      json_system_data = json.load(system)
      return json_system_data


def getBrokerAppConfig():
    with open('../config/brokerapp.json', 'r') as brokerapp:
      jsonUserData = json.load(brokerapp)
      return jsonUserData


def get_holidays():
    with open('../config/holidays.json', 'r') as holidays:
      holidaysData = json.load(holidays)
      return holidaysData

def get_boolean_env(name, default):
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in ['true', 'yes', '1']

# The following code changes are not active yet. Will integrate them once we are done with the trade manager development.

class BaseConfig:
    
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    '''
    DEBUG = get_boolean_env('FLASK_DEBUG', False)
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'not-secret-key')  # FIXME
    STRICT_SLASHES = False
    BUNDLES = BUNDLES
    
    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.Redis(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_REDIS_PORT', 6379)),
    )
    SESSION_PROTECTION = 'strong'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # SECURITY_TOKEN_MAX_AGE is fixed from time of token generation;
    # it does not update on refresh like a session timeout would. for that,
    # we set (the ironically named) PERMANENT_SESSION_LIFETIME
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALEMBIC = {
        'script_location': os.path.join(PROJECT_ROOT, 'migrations'),
    }

    ##########################################################################
    # celery                                                                 #
    ##########################################################################
    CELERY_BROKER_URL = 'redis://{host}:{port}/0'.format(
        host=os.getenv('FLASK_REDIS_HOST', '127.0.0.1'),
        port=os.getenv('FLASK_REDIS_PORT', 6379),
    )
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ('json', 'pickle')

    ##########################################################################
    # mail                                                                   #
    ##########################################################################
    MAIL_ADMINS = ('admin@example.com',)  # FIXME
    MAIL_SERVER = os.environ.get('FLASK_MAIL_HOST', 'localhost')
    MAIL_PORT = int(os.environ.get('FLASK_MAIL_PORT', 25))
    MAIL_USE_TLS = get_boolean_env('FLASK_MAIL_USE_TLS', False)
    MAIL_USE_SSL = get_boolean_env('FLASK_MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('FLASK_MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('FLASK_MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = (
        os.environ.get('FLASK_MAIL_DEFAULT_SENDER_NAME', 'Flask React SPA'),
        os.environ.get('FLASK_MAIL_DEFAULT_SENDER_EMAIL',
                       f"noreply@{os.environ.get('FLASK_DOMAIN', 'localhost')}")
    )
    
    ##########################################################################
    # security                                                               #
    ##########################################################################
    SECURITY_DATETIME_FACTORY = utcnow

    # specify which user field attributes can be used for login
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email', 'username']

    # NOTE: itsdangerous "salts" are not normal salts in the cryptographic
    # sense, see https://pythonhosted.org/itsdangerous/#the-salt
    SECURITY_PASSWORD_SALT = os.environ.get('FLASK_SECURITY_PASSWORD_SALT',
                                            'security-password-salt')

    # disable flask-security's use of .txt templates (instead we
    # generate the plain text from the html message)
    SECURITY_EMAIL_PLAINTEXT = False

    # enable forgot password functionality
    SECURITY_RECOVERABLE = True

    # enable email confirmation before allowing login
    SECURITY_CONFIRMABLE = True

    # this setting is parsed as a kwarg to timedelta, so the time unit must
    # always be plural
    SECURITY_CONFIRM_EMAIL_WITHIN = '7 days'  # default 5 days

    # urls for the *frontend* router
    SECURITY_CONFIRM_ERROR_VIEW = '/sign-up/resend-confirmation-email'
    SECURITY_POST_CONFIRM_VIEW = '/?welcome'
    
    '''
    pass


class DevConfig(BaseConfig):
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    ENV = 'dev'
    DEBUG = get_boolean_env('FLASK_DEBUG', True)
    # EXPLAIN_TEMPLATE_LOADING = True

    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_COOKIE_SECURE = False

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=os.environ.get('FLASK_DATABASE_USER', 'flask_api'),
        password=os.environ.get('FLASK_DATABASE_PASSWORD', 'flask_api'),
        host=os.environ.get('FLASK_DATABASE_HOST', '127.0.0.1'),
        port=os.environ.get('FLASK_DATABASE_PORT', 5432),
        db_name=os.environ.get('FLASK_DATABASE_NAME', 'flask_api'),
    )
    # SQLALCHEMY_ECHO = True

    ##########################################################################
    # mail                                                                   #
    ##########################################################################
    MAIL_PORT = 1025  # MailHog
    MAIL_DEFAULT_SENDER = ('Flask React SPA', 'noreply@localhost')

    ##########################################################################
    # security                                                               #
    ##########################################################################
    SECURITY_CONFIRMABLE = True
    SECURITY_CONFIRM_EMAIL_WITHIN = '1 minutes'  # for testing

    pass


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # :memory:

    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH_OPTIONS = dict(bcrypt={'rounds': 4})
    SECURITY__SEND_MAIL_TASK = None
    
    pass
  
  
class ProdConfig(BaseConfig):
    ##########################################################################
    # flask                                                                  #
    ##########################################################################
    ENV = 'prod'
    DEBUG = get_boolean_env('FLASK_DEBUG', False)

    ##########################################################################
    # database                                                               #
    ##########################################################################
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=os.environ.get('FLASK_DATABASE_USER', 'flask_api'),
        password=os.environ.get('FLASK_DATABASE_PASSWORD', 'flask_api'),
        host=os.environ.get('FLASK_DATABASE_HOST', '127.0.0.1'),
        port=os.environ.get('FLASK_DATABASE_PORT', 5432),
        db_name=os.environ.get('FLASK_DATABASE_NAME', 'flask_api'),
    )

    ##########################################################################
    # session/cookies                                                        #
    ##########################################################################
    SESSION_COOKIE_DOMAIN = os.environ.get(
        'FLASK_DOMAIN', 'example.com')  # FIXME
    SESSION_COOKIE_SECURE = get_boolean_env('SESSION_COOKIE_SECURE', True)
    
    pass
