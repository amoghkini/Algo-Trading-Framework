import logging

from brokers.brokers import Brokers
from common.login_methods import LoginMethods
from loginmgmt.zerodha_login import ZerodhaLogin
from loginmgmt.zerodha_web_login import ZerodhaWebLogin
from models.broker_app_details import BrokerAppDetails

class Controller:
    broker_login = None # static variable
    broker_name = None # static variable

    def handle_broker_login(args,broker_values):
        broker_app_details = BrokerAppDetails(broker_values.get('broker_name'))
        broker_app_details.set_client_id(broker_values.get('broker_id'))
        broker_app_details.set_app_key(broker_values.get('broker_id'))
        broker_app_details.set_app_secret(broker_values.get('broker_id'))
        
        logging.info('handle_broker_login app_key %s',broker_app_details.app_key)
        Controller.broker_name = broker_app_details.broker
        try:
            if broker_values.get('login_method') == LoginMethods.API_WITH_BROKER_PORTAL:
                if Controller.broker_name == Brokers.ZERODHA:
                    Controller.broker_login = ZerodhaLogin(broker_app_details)
                # Other brokers - not implemented
                # elif Controller.broker_name == Brokers.FYRES:
                #    Controller.broker_login = FyersLogin(broker_app_details)
            
            elif broker_values.get('login_method') in (LoginMethods.CREDS_WITH_ENC_TOKEN, LoginMethods.CREDS_WITHOUT_ENC_TOKEN):
                if Controller.broker_name == Brokers.ZERODHA:
                    Controller.broker_login = ZerodhaWebLogin(broker_app_details)
                # Other brokers - not implemented
                # elif Controller.broker_name == Brokers.FYRES:
                #    Controller.broker_login = FyersLogin(broker_app_details)
                
        except Exception as e:
            print("Exception occured",e)
          
        redirect_url = Controller.broker_login.login(args, broker_values)
        print("Redirect url", redirect_url)
        return redirect_url

    def get_broker_login():
        return Controller.broker_login

    def get_broker_name():
        return Controller.broker_name
