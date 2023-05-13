import os
from typing import Dict, Tuple

from flask import Flask, g, session

from app.endpoints import register_endpoints
from app.error_handlers import register_error_handlers
from app.server_bootup_operations import server_bootup_operations
from common.execution_env import ExecutionEnv
from config.config import BaseConfig, TEMPLATE_FOLDER, STATIC_FOLDER, get_server_config
from database.database_connection import get_db
from utils.logger import config_root_logger
from utils.utils import Utils


def create_app() -> Flask:
    
    server_bootup_validations()
    
    config_object: BaseConfig = Utils.get_config()
    app = _create_app(config_object,
                      template_folder=TEMPLATE_FOLDER,
                      static_folder=STATIC_FOLDER)
    return app


def _create_app(config_object: BaseConfig, **kwargs) -> Flask:
    app = Flask(__name__, **kwargs)
    configure_app(app, config_object)
    register_endpoints(app)
    register_error_handlers(app)      
    return app


def configure_app(app: Flask, config_object: BaseConfig) -> None:
    #configure configuration
    app.config.from_object(config_object)
    
    configure_requests(app)  # configure requests
    configure_logger()  # configure logger



    
def configure_requests(app: Flask) -> None:
    @app.before_first_request
    def before_first_request():
        server_bootup_operations()
    
    @app.before_request
    def before_request():
        session.permanent = True  # set session to use PERMANENT_SESSION_LIFETIME
        session.modified = True   # reset the session timer on every request
        #app.permanent_session_lifetime = timedelta(minutes=60)

        g.user = None
        if 'user' in session:
            g.user = session['user']

        g.secret_key = "Amogh kini"
        g.db = get_db()


    @app.teardown_appcontext
    def shutdown_session(exception=None) -> None:
        db = g.pop('db', None)
        
            
    @app.after_request
    def after_request(response):
        return response

    
def configure_logger() -> None:
    log_file_dir: str = Utils.get_log_dir()
    date_time_str: str = Utils.get_today_date_str(time=True)
    log_file_dir_with_date: str = os.path.join(log_file_dir, Utils.get_today_date_str())
    if os.path.exists(log_file_dir_with_date) == False:
        os.makedirs(log_file_dir_with_date)
        print("New directory created==>", log_file_dir_with_date)
    config_root_logger(log_file_dir_with_date + "/app_{0}.log".format(date_time_str))


def server_bootup_validations() -> None:
    validate_and_create_directory()
    validate_execution_env()


def validate_and_create_directory() -> None:
    server_config: Dict = get_server_config()
    
    log_file_dir: str = server_config.get('logFileDir')

    if os.path.exists(log_file_dir) == False:
        print("Log File Directory " + log_file_dir.lstrip('..') + \
          " does not exist. Creating the log directory.")
        os.makedirs(log_file_dir)
        if os.path.exists(log_file_dir) == False:
            print("Failed to create the Log file directory. " \
                  "Exiting the application.")
            exit(-1)

    deploy_dir: str = server_config.get('deployDir')
    if os.path.exists(deploy_dir) == False:
        print("Deploy Directory " + deploy_dir.lstrip('..') + \
              " does not exist. Creating the deploy directory.")
        os.makedirs(deploy_dir)
        if os.path.exists(deploy_dir) == False:
            print("Failed to create the deploy directory." \
                  "Exiting the application.")
            exit(-1)
        
        
def validate_execution_env() -> None:
    env: str = Utils.get_execution_env()
    
    valid_executions: Tuple = (ExecutionEnv.DEV, ExecutionEnv.TEST, ExecutionEnv.PROD)
    if env not in valid_executions:
        print("The execution environment ", env, "is not valid!!!.")
        print("The valid executions are ", valid_executions)
        exit(1)