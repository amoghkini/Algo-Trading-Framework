import logging

from broker.brokers import Brokers
from broker_transaction_management_system.base_transaction_manager import BaseTransactionManager

class ZerodhaTransactionManager(BaseTransactionManager):
    
    def __init__(self) -> None:
        super().__init__(Brokers.ZERODHA)
        
    def test_connection(self):
        logging.info('%s: Going to test the broker connection',self.broker)
        kite = self.broker_handle
        try:
            profile = kite.profile()
            return profile
        except Exception as e:
            logging.info('%s Broker Connection failed: %s', self.broker, str(e))
            raise Exception(str(e))
