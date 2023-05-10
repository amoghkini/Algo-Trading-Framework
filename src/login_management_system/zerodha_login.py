import logging
from kiteconnect import KiteConnect

from login_management_system.base_login import BaseLogin

class ZerodhaLogin(BaseLogin):
    def __init__(self, broker_app_details):
        BaseLogin.__init__(self, broker_app_details)

    def login(self, args, broker_details):
        logging.info('==> ZerodhaLogin .args => %s', args)
        
        broker_handle = KiteConnect(api_key=self.broker_app_details.app_key)
        redirect_url = None
        access_token: str = broker_details.get('access_token')
        if access_token:   # and test_connection()  # To be implemented: Check connection to verify the access token generated for the day is still valid
            self.set_broker_handle(broker_handle)
            self.set_access_token(access_token)
            redirect_url = None
        else:
            if 'request_token' in args:
                request_token = args['request_token']
                logging.info('Zerodha requestToken = %s', request_token)
                session = broker_handle.generate_session(
                    request_token, api_secret=self.broker_app_details.app_secret)
                
                access_token = session['access_token']
                access_token = access_token
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

