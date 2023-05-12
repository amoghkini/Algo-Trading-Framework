import logging
import broker.broker_methods as broker_methods

from kiteconnect import KiteConnect
from kiteconnect.exceptions import TokenException
from login_management_system.base_login import BaseLogin

class ZerodhaLogin(BaseLogin):
    def __init__(self, broker_app_details):
        BaseLogin.__init__(self, broker_app_details)

    def login(self, args, broker_details):
        logging.info('==> ZerodhaLogin .args => %s', args)
        broker_handle = KiteConnect(api_key=self.broker_app_details.app_key)
        redirect_url = None
        # The following code is written to check if we already have valid acceess token. 
        # This code is written to avoid frequent login requests while using kite extensions.
        # We may not required this code while using API. We will check this and remove it during testing.
        access_token: str = broker_details.get('access_token')
        if access_token:
            broker_handle.set_headers(access_token.split('&')[0], broker_details.get('broker_id'))
            self.set_broker_handle(broker_handle)
            self.set_access_token(access_token)
            try:
                broker_profile = broker_methods.BrokerMethods.get_transaction_manager().test_connection()
                redirect_url = None
            except TokenException as e:
                logging.info("The provided api key or access token is invalid. Need to login once again.")
                redirect_url = self.__login(args, broker_details, broker_handle)
            except Exception as e:
                logging.info("Something went wrong while testing broker conection. Need to login once again.q")
                redirect_url = self.__login(args, broker_details, broker_handle)
        else:
            redirect_url = self.__login(args, broker_details, broker_handle)
        return redirect_url
    
    def __login(self, args, broker_values,  broker_handle):
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

