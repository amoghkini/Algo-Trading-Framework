import logging

from brokers.brokers import Brokers
from common.login_methods import LoginMethods
from config.config import getBrokerAppConfig
from loginmgmt.zerodha_login import ZerodhaLogin
from loginmgmt.zerodha_web_login import ZerodhaWebLogin
from models.broker_app_details import BrokerAppDetails

class Controller:
    brokerLogin = None # static variable
    brokerName = None # static variable

    def handleBrokerLogin(args,broker_values):
        brokerAppConfig = getBrokerAppConfig()
        brokerAppDetails = BrokerAppDetails(broker_values.get('broker_name'))
        brokerAppDetails.setClientID(broker_values.get('broker_id'))
        brokerAppDetails.setAppKey(broker_values.get('broker_id'))
        brokerAppDetails.setAppSecret(broker_values.get('broker_id'))
        
        logging.info('handleBrokerLogin appKey %s', brokerAppDetails.appKey)
        Controller.brokerName = brokerAppDetails.broker
        try:
            if broker_values.get('login_method') == LoginMethods.API_WITH_BROKER_PORTAL:
                if Controller.brokerName == Brokers.ZERODHA:
                    Controller.brokerLogin = ZerodhaLogin(brokerAppDetails)
                # Other brokers - not implemented
                # elif Controller.brokerName == Brokers.FYRES:
                #    Controller.brokerLogin = FyersLogin(brokerAppDetails)
            
            elif broker_values.get('login_method') in (LoginMethods.CREDS_WITH_ENC_TOKEN, LoginMethods.CREDS_WITHOUT_ENC_TOKEN):
                if Controller.brokerName == Brokers.ZERODHA:
                    Controller.brokerLogin = ZerodhaWebLogin(brokerAppDetails)
                # Other brokers - not implemented
                # elif Controller.brokerName == Brokers.FYRES:
                #    Controller.brokerLogin = FyersLogin(brokerAppDetails)
                
        except Exception as e:
            print("Exception occured",e)
          
        redirectUrl = Controller.brokerLogin.login(args, broker_values)
        print("Redirect url",redirectUrl)
        return redirectUrl

    def getBrokerLogin():
        return Controller.brokerLogin

    def getBrokerName():
        return Controller.brokerName
