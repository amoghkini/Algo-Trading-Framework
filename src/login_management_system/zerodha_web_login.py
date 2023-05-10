import logging

from broker.broker_login_methods import BrokerLoginMethods
from broker_web_extenstions.kiteext import KiteExt
from login_management_system.base_login import BaseLogin

class ZerodhaWebLogin(BaseLogin):
    def __init__(self, broker_app_details):
        BaseLogin.__init__(self, broker_app_details)

    def login(self, args, broker_details):
        logging.info('==> ZerodhaWebLogin .args => %s', args)
        
        broker_handle = KiteExt()
        redirect_url = None
        access_token: str = broker_details.get('access_token')
        if access_token:   # and test_connection()  # To be implemented: Check connection to verify the access token generated for the day is still valid
            self.set_broker_handle(broker_handle)
            self.set_access_token(access_token)
            redirect_url = None
        else:
            if 'login_required' in args:
                if broker_details.get('login_method') == BrokerLoginMethods.CREDS_WITHOUT_ENC_TOKEN:
                    broker_handle.login_with_credentials(broker_details.get('broker_id'), broker_details.get('password'), broker_details.get('totp_key'))
                
                elif broker_details.get('login_method') == BrokerLoginMethods.CREDS_WITH_ENC_TOKEN:
                    try:
                        broker_handle.set_headers(broker_details.get('encryption_token'))
                    except Exception as e:
                        raise
                    
                print(broker_handle.profile())
                access_token = broker_handle.enctoken+"&user_id="+broker_handle.user_id
                
                logging.info('access token = %s', access_token)
                logging.info('Login successful. access token = %s', access_token)
                
                logging.info('Zerodha access_token = %s', access_token)
                broker_handle.set_access_token(access_token)

                logging.info('Zerodha Login successful. access_token = %s', access_token)

                # set broker handle and access token to the instance
                self.set_broker_handle(broker_handle)
                self.set_access_token(access_token)
                redirect_url = None
            else:
                login_url = broker_handle.login_url()
                logging.info('Redirecting to zerodha login url = %s', login_url)
                redirect_url = login_url
        return redirect_url
    
    def logout(self):
        # To be implemented
        return
