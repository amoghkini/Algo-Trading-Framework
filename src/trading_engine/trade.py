import logging

from models.product_type import ProductType
from trading_engine.trade_state import TradeState
from utils.time_utils import TimeUtils
from utils.utils import Utils

class Trade:
    def __init__(self, trading_symbol = None):
        self.exchange = "NSE" 
        self.trade_id = Utils.generate_trade_id()  # Unique ID for each trade
        self.trading_symbol = trading_symbol
        self.strategy = ""
        self.direction = ""
        self.product_type = ProductType.MIS
        self.is_futures = False # Futures trade
        self.is_options = False # Options trade
        self.option_type = None # CE/PE. Applicable only if isOptions is True
        self.place_market_order = False # True means place the entry order with Market Order Type
        self.intraday_square_off_timestamp = None # Can be strategy specific. Some can square off at 15:00:00 some can at 15:15:00 etc.
        self.requested_entry = 0 # Requested entry
        self.entry = 0 # Actual entry. This will be different from requestedEntry if the order placed is Market order
        self.qty = 0 # Requested quantity
        self.filled_qty = 0 # In case partial fill qty is not equal to filled quantity
        self.initial_stop_loss = 0 # Initial stop loss
        self.stop_loss = 0 # This is the current stop loss. In case of trailing SL the current stopLoss and initialStopLoss will be different after some time
        self.target = 0 # Target price if applicable
        self.cmp = 0 # Last traded price

        self.trade_state = TradeState.CREATED # state of the trade
        self.timestamp = None # Set this timestamp to strategy timestamp if you are not sure what to set
        self.create_timestamp = TimeUtils.get_epoch() # Timestamp when the trade is created (Not triggered)
        self.start_timestamp = None # Timestamp when the trade gets triggered and order placed
        self.end_timestamp = None # Timestamp when the trade ended
        self.pnl = 0 # Profit loss of the trade. If trade is Active this shows the unrealized pnl else realized pnl
        self.pnl_percentage = 0 # Profit Loss in percentage terms
        self.exit = 0 # Exit price of the trade
        self.exit_reason = None # SL/Target/SquareOff/Any Other
        
        self.entry_order = None # Object of Type ordermgmt.Order
        self.sl_order = None # Object of Type ordermgmt.Order
        self.target_order = None # Object of Type ordermgmt.Order

    def equals(self, trade): # compares to trade objects and returns True if equals
        if trade == None:
            return False
        if self.trade_id == trade.trade_id:
            return True
        if self.trading_symbol != trade.trading_symbol:
            return False
        if self.strategy != trade.strategy:
            return False  
        if self.direction != trade.direction:
            return False
        if self.product_type != trade.product_type:
            return False
        if self.requested_entry != trade.requested_entry:
            return False
        if self.qty != trade.qty:
            return False
        if self.timestamp != trade.timestamp:
            return False
        return True

    def __str__(self):
        return "ID=" + str(self.trade_id) + ", state=" + self.trade_state + ", symbol=" + self.trading_symbol \
          + ", strategy=" + self.strategy + ", direction=" + self.direction \
          + ", product_type=" + self.product_type + ", requested_entry=" + str(self.requested_entry) \
          + ", stop_loss=" + str(self.stop_loss) + ", target=" + str(self.target) \
          + ", entry=" + str(self.entry) + ", exit=" + str(self.exit) \
          + ", profitLoss" + str(self.pnl)

