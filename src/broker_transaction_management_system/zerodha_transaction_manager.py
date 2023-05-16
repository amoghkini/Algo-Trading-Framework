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

    def get_orders(self):
        logging.info('%s: Going to fetch the user orders', self.broker)
        kite = self.broker_handle
        try:
            orders = kite.orders()
            return orders
        except Exception as e:
            logging.info('%s Failed to fetch the orders: %s',self.broker, str(e))
            raise Exception(str(e))

    def get_positions(self):
        logging.info('%s: Going to fetch the user positions', self.broker)
        kite = self.broker_handle
        try:
            positions = kite.positions()
            return positions
        except Exception as e:
            logging.info('%s Failed to fetch the positions: %s',self.broker, str(e))
            raise Exception(str(e))

    def get_holdings(self):
        logging.info('%s: Going to fetch the user holdings', self.broker)
        kite = self.broker_handle
        try:
            holdings = kite.holdings()
            return holdings
        except Exception as e:
            logging.info('%s Failed to fetch the holdings: %s',self.broker, str(e))
            raise Exception(str(e))
