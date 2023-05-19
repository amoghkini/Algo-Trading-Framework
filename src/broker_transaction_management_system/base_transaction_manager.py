from core.controller import Controller

class BaseTransactionManager:
    def __init__(self, broker: str) -> None:
        self.broker = broker
        self.broker_handle = Controller.get_broker_login().get_broker_handle()

    def test_connection(self):
        pass
    
    def get_orders(self):
        pass
    
    def get_positions(self):
        pass
    
    def get_holdings(self):
        pass