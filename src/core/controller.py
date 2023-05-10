import logging

import broker.broker_methods as broker_methods
from broker.broker_login_methods import BrokerLoginMethods
from broker.brokers import Brokers
from login_management.zerodha_login import ZerodhaLogin
from login_management.zerodha_web_login import ZerodhaWebLogin
from models.broker_app_details import BrokerAppDetails
from utils.utils import Utils

class Controller:
    broker_login = None # static variable
    broker_name = None # static variable

    def handle_broker_login(args,broker_values):
        broker_app_details = BrokerAppDetails(broker_values.get('broker_name'))
        broker_app_details.set_client_id(broker_values.get('broker_id'))
        broker_app_details.set_app_key(broker_values.get('app_key'))
        broker_app_details.set_app_secret(broker_values.get('app_secret_key'))
        logging.info('handle_broker_login app_key %s',broker_app_details.app_key)
        Controller.broker_name = broker_app_details.broker
        try:
            if broker_values.get('login_method') == BrokerLoginMethods.API_WITH_BROKER_PORTAL:
                if Controller.broker_name == Brokers.ZERODHA:
                    Controller.broker_login = ZerodhaLogin(broker_app_details)
                # elif Controller.broker_name == Brokers.FYRES:
                #    Controller.broker_login = FyersLogin(broker_app_details)

            elif broker_values.get('login_method') in (BrokerLoginMethods.CREDS_WITH_ENC_TOKEN, BrokerLoginMethods.CREDS_WITHOUT_ENC_TOKEN):
                if Controller.broker_name == Brokers.ZERODHA:
                    Controller.broker_login = ZerodhaWebLogin(broker_app_details)
                #elif Controller.broker_name == Brokers.FYRES:
                #    Controller.broker_login = FyersLogin(broker_app_details)

            # Read the access token from database and pass it to login method to check if it is still valid.
            access_token: str = broker_methods.BrokerMethods.get_access_token(broker_values.get('broker_id'))
            broker_values['access_token'] = access_token    
            
            redirect_url = Controller.broker_login.login(args, broker_values)
        
            # The redirect_url None indicates that access token is available. Write it in access_tokens table.
            if not redirect_url:
                new_access_token: str = Controller.broker_login.get_access_token()
                # If new and old access token is different then only table write operation is called.
                if access_token != new_access_token:
                    access_token_data = {
                        "broker_id": broker_app_details.client_id,
                        "token_date": Utils.get_today_date_str(),
                        "broker_name": broker_app_details.broker,
                        "access_token": new_access_token
                    }
                    broker_methods.BrokerMethods.save_access_token(access_token_data)            
            return redirect_url
        except Exception as e:
            raise e
        
    def get_broker_login():
        return Controller.broker_login

    def get_broker_name():
        return Controller.broker_name
