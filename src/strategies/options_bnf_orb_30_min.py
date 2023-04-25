import logging
from datetime import datetime

from instruments.instruments import Instruments
from models.direction import Direction
from models.product_type import ProductType
from strategies.base_strategy import BaseStrategy
from trademgmt.trade import Trade
from trademgmt.trade_manager import TradeManager
from utils.utils import Utils

# Each strategy has to be derived from BaseStrategy
class BNFORB30Min(BaseStrategy):
    __instance = None

    @staticmethod
    def get_instance():  # singleton class
        if BNFORB30Min.__instance == None:
            BNFORB30Min()
        return BNFORB30Min.__instance

    def __init__(self):
        if BNFORB30Min.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BNFORB30Min.__instance = self
        # Call Base class constructor
        super().__init__("BNFORB30Min")
        # Initialize all the properties specific to this strategy
        self.product_type = ProductType.MIS
        self.symbols = []
        self.sl_percentage = 0
        self.target_percentage = 0
        self.start_timestamp = Utils.get_time_of_today(9, 45, 0) # When to start the strategy. Default is Market start time
        self.stop_timestamp = Utils.get_time_of_today(14, 30, 0) # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = Utils.get_time_of_today(15, 0, 0) # Square off time
        self.capital = 100000 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 0
        self.max_trades_per_day = 1  # Max number of trades per day under this strategy
        self.is_fno = True  # Does this strategy trade in FnO or not
        self.capital_per_set = 100000 # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)

    def process(self):
        now = datetime.now()
        process_end_time = Utils.get_time_of_today(9, 50, 0)
        if now < self.start_timestamp:
            return
        if now > process_end_time:
            # We are interested in creating the symbol only between 09:45 and 09:50 
            # since we are not using historical candles so not aware of exact high and low of the first 30 mins
            return

        if len(self.trades) >= 2:
            return

        symbol = Utils.prepare_monthly_expiry_futures_symbol('BANKNIFTY')
        quote = self.get_quote(symbol)
        if quote == None:
            logging.error('%s: Could not get quote for %s', self.get_name(), symbol)
            return
        
        logging.info('%s: %s => last_traded_price = %f', self.get_name(), symbol, quote.last_traded_price)
        self.generate_trade(symbol, Direction.LONG, quote.high, quote.low)
        self.generate_trade(symbol, Direction.SHORT, quote.high, quote.low)

    def generate_trade(self, trading_symbol, direction, high, low):
        trade = Trade(trading_symbol)
        trade.strategy = self.get_name()
        trade.is_futures = True
        trade.direction = direction
        trade.product_type = self.product_type
        trade.place_market_order = True
        trade.requested_entry = high if direction == Direction.LONG else low
        trade.timestamp = Utils.get_epoch(self.start_timestamp) # setting this to strategy timestamp
        # Calculate lots
        num_lots = self.calculate_lots_per_trade()
        isd = Instruments.get_instrument_data_by_symbol(trading_symbol)  # Get instrument data to know qty per lot
        trade.qty = isd['lot_size'] * num_lots
        
        trade.stop_loss = low if direction == Direction.LONG else high
        sl_diff = high - low
        # target is 1.5 times of SL
        if direction == 'LONG':
            trade.target = Utils.round_to_nse_price(trade.requested_entry + 1.5 * sl_diff)
        else:
            trade.target = Utils.round_to_nse_price(trade.requested_entry - 1.5 * sl_diff)

        trade.intraday_square_off_timestamp = Utils.get_epoch(self.square_off_timestamp)
        # Hand over the trade to TradeManager
        TradeManager.add_new_trade(trade)

    def should_place_trade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if super().should_place_trade(trade, tick) == False:
            return False

        if tick == None:
            return False
        
        if trade.direction == Direction.LONG and tick.last_traded_price > trade.requested_entry:
            return True
        elif trade.direction == Direction.SHORT and tick.last_traded_price < trade.requested_entry:
            return True
        return False
