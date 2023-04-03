import logging
from flask import request

from common.login_methods import LoginMethods
from config.config import get_system_config
from loginmgmt.base_login import BaseLogin
from brokers.kiteext import KiteExt

class ZerodhaWebLogin(BaseLogin):
    def __init__(self, brokerAppDetails):
        BaseLogin.__init__(self, brokerAppDetails)

    def login(self, args, broker_details):
        logging.info('==> ZerodhaWebLogin .args => %s', args)
        
        systemConfig = get_system_config()
        brokerHandle = KiteExt()
        redirectUrl = None
        print("Amogh inside login method")
        print("args",args)
        print("Form Zerodha web login", broker_details)
        if 'loginRequired' in args:
            print("Amogh inside login required args",brokerHandle)
            
            if broker_details.get('login_method') == LoginMethods.CREDS_WITHOUT_ENC_TOKEN:
                brokerHandle.login_with_credentials(broker_details.get('broker_id'), broker_details.get('password'), broker_details.get('totp_key'))
            
            elif broker_details.get('login_method') == LoginMethods.CREDS_WITH_ENC_TOKEN:
                #brokerHandle.set_headers(broker_details.get('encryption_token'), broker_details.get('broker_id'))
                try:
                    brokerHandle.set_headers(broker_details.get('encryption_token'))
                except ValueError as e:
                    print("Value error",e)
                except Exception as e:
                    print("Exception occured",e)
                
            print(brokerHandle.profile())
            access_token = brokerHandle.enctoken+"&user_id="+brokerHandle.user_id
            
            logging.info('access token = %s', access_token)
            logging.info('Login successful. access token = %s', access_token)
            print(access_token)
            
            logging.info('Zerodha accessToken = %s', access_token)
            brokerHandle.set_access_token(access_token)

            logging.info('Zerodha Login successful. accessToken = %s', access_token)

            # set broker handle and access token to the instance
            self.setBrokerHandle(brokerHandle)
            self.setAccessToken(access_token)
            
            
            
            '''
            # redirect to home page with query param loggedIn=true
            homeUrl = systemConfig['homeUrl'] + '?loggedIn=true'
            logging.info('Zerodha Redirecting to home page %s', homeUrl)
            '''
            redirectUrl = None
        else:
            loginUrl = brokerHandle.login_url()
            logging.info('Redirecting to zerodha login url = %s', loginUrl)
            redirectUrl = loginUrl

        return redirectUrl
    
    def logout(self):
        return
