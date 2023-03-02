import logging

from brokers.Brokers import Brokers
from common.LoginMethods import LoginMethods
from config.Config import getBrokerAppConfig
from models.BrokerAppDetails import BrokerAppDetails
from loginmgmt.ZerodhaLogin import ZerodhaLogin
from loginmgmt.ZerodhaWebLogin import ZerodhaWebLogin

class Controller:
  brokerLogin = None # static variable

  def handleBrokerLogin(args,broker_values):
    brokerAppConfig = getBrokerAppConfig()
    
    brokerAppDetails = BrokerAppDetails(broker_values.get('broker_name'))
    brokerAppDetails.setClientID(broker_values.get('broker_id'))
    brokerAppDetails.setAppKey(broker_values.get('broker_id'))
    brokerAppDetails.setAppSecret(broker_values.get('broker_id'))
    
    logging.info('handleBrokerLogin appKey %s', brokerAppDetails.appKey)
    
    try:
      if broker_values.get('login_method') == LoginMethods.API_WITH_BROKER_PORTAL:
        if brokerAppDetails.broker == Brokers.ZERODHA:
          Controller.brokerLogin = ZerodhaLogin(brokerAppDetails)
      
      elif broker_values.get('login_method') in (LoginMethods.CREDS_WITH_ENC_TOKEN, LoginMethods.CREDS_WITHOUT_ENC_TOKEN):
        if brokerAppDetails.broker == Brokers.ZERODHA:
          Controller.brokerLogin = ZerodhaWebLogin(brokerAppDetails)
          
      # Other brokers - not implemented
      #elif brokerAppDetails.broker == 'fyers':
        #Controller.brokerLogin = FyersLogin(brokerAppDetails)
    except Exception as e:
      print("Exception occured",e)
      

    redirectUrl = Controller.brokerLogin.login(args, broker_values)
    print("Redirect url",redirectUrl)
    return redirectUrl

  def getBrokerLogin():
    return Controller.brokerLogin
