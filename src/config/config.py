import json
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv('../.env')

APP_NAME = "Algo Trading Framework"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')

def get_server_config():
    with open('../config/server.json', 'r') as server:
        json_server_data = json.load(server)
        return json_server_data

def get_holidays():
    with open('../config/holidays.json', 'r') as holidays:
        holidays_data = json.load(holidays)
        return holidays_data

def get_timestamps_data():
    server_config = get_server_config()
    timestamps_file_path = os.path.join(server_config['deployDir'], 'timestamps.json')
    if os.path.exists(timestamps_file_path) == False:
        return {}
    timestamps_file = open(timestamps_file_path, 'r')
    timestamps = json.loads(timestamps_file.read())
    return timestamps

def save_timestamps_data(timestamps = {}):
    server_config = get_server_config()
    timestamps_file_path = os.path.join(server_config['deployDir'], 'timestamps.json')
    with open(timestamps_file_path, 'w') as timestamps_file:
        json.dump(timestamps, timestamps_file, indent=2)
    print("saved timestamps data to file " + timestamps_file_path)

def get_env():
    return get_server_config().get('env')


class BaseConfig(object):
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY','This is secret key')
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=get_server_config().get('sessionLifetime'))

class ProdConfig(BaseConfig):

    ENV = 'prod'
    DEBUG = True if get_env() == 'dev' else False

    # Database Credentials


class DevConfig(BaseConfig):
    ENV =  'dev'
    DEBUG = True if get_env() == 'dev' else False
    
class TestingConfig(BaseConfig):
    ENV = 'qa'
    DEBUG = True if get_env() == 'dev' else False
