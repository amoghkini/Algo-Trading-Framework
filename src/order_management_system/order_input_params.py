from models.product_type import ProductType
from models.segment import Segment

class OrderInputParams:
    def __init__(self, trading_symbol):
        self.exchange = "NSE" # default
        self.is_fno = False
        self.segment = Segment.EQUITY # default
        self.product_type = ProductType.MIS # default
        self.trading_symbol = trading_symbol
        self.direction = ""
        self.order_type = "" # One of the values of ordermgmt.OrderType
        self.qty = 0
        self.price = 0
        self.trigger_price = 0 # Applicable in case of SL order

    def __str__(self):
        return "symbol=" + str(self.trading_symbol) + ", exchange=" + self.exchange \
            + ", product_type=" + self.product_type + ", segment=" + self.segment \
            + ", direction=" + self.direction + ", order_type=" + self.order_type \
            + ", qty=" + str(self.qty) + ", price=" + str(self.price) + ", trigger_price=" + str(self.trigger_price) \
            + ", isFnO=" + str(self.is_fno)
