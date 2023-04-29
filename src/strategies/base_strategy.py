import logging
import time
from datetime import datetime

from core.quotes import Quotes
from models.product_type import ProductType
from trading_engine.trade_manager import TradeManager
from utils.utils import Utils

class BaseStrategy:
    def __init__(self, name):
        # NOTE: All the below properties should be set by the Derived Class (Specific to each strategy)
        self.name = name # strategy name
        self.enabled = True # Strategy will be run only when it is enabled
        self.product_type = ProductType.MIS # MIS/NRML/CNC etc
        self.symbols = [] # List of stocks to be traded under this strategy
        self.sl_percentage = 0
        self.target_percentage = 0
        self.start_timestamp = Utils.get_market_start_time() # When to start the strategy. Default is Market start time
        self.stop_timestamp = None # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = None # Square off time
        self.capital = 10000 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 1 # 2x, 3x Etc
        self.max_trades_per_day = 1 # Max number of trades per day under this strategy
        self.is_fno = False # Does this strategy trade in FnO or not
        self.capital_per_set = 0 # Applicable if isFnO is True (Set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        
        TradeManager.register_strategy(self) # Register strategy with trade manager
        self.trades = TradeManager.get_all_trades_by_strategy(self.name) # Load all trades of this strategy into self.trades on restart of app

    def get_name(self):
        return self.name

    def is_enabled(self):
        return self.enabled

    def set_disabled(self):
        self.enabled = False

    def process(self):
        # Implementation is specific to each strategy - To defined in derived class
        logging.info("BaseStrategy process is called.")
        pass

    def calculate_capital_per_trade(self):
        leverage = self.leverage if self.leverage > 0 else 1
        capital_per_trade = int(self.capital * leverage / self.max_trades_per_day)
        return capital_per_trade

    def calculate_lots_per_trade(self):
        if self.is_fno == False:
            return 0
        # Applicable only for fno
        return int(self.capital / self.capital_per_set)

    def can_trade_today(self):
        # Derived class should override the logic if the strategy to be traded only on specific days of the week
        return True

    def run(self):
        # NOTE: This should not be overriden in Derived class
        if self.enabled == False:
            logging.warn("%s: Not going to run strategy as its not enabled.", self.get_name())
            return

        if Utils.is_market_closed_for_the_day():
            logging.warn("%s: Not going to run strategy as market is closed.", self.get_name())
            return

        now = datetime.now()
        if now < Utils.get_market_start_time():
            Utils.wait_till_market_opens(self.get_name())

        if self.can_trade_today() == False:
            logging.warn("%s: Not going to run strategy as it cannot be traded today.", self.get_name())
            return

        if now < self.start_timestamp:
            wait_seconds = Utils.get_epoch(self.start_timestamp) - Utils.get_epoch(now)
            logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...", self.get_name(), wait_seconds)
            if wait_seconds > 0:
                time.sleep(wait_seconds)

        # Run in an loop and keep processing
        while True:
            if Utils.is_market_closed_for_the_day():
                logging.warn("%s: Exiting the strategy as market closed.", self.get_name())
                break

            # Derived class specific implementation will be called when process() is called
            self.process()

            # Sleep and wake up on every 30th second
            now = datetime.now()
            wait_seconds = 30 - (now.second % 30) 
            time.sleep(wait_seconds)

    def should_place_trade(self, trade, tick):
        # Each strategy should call this function from its own should_place_trade() method before working on its own logic
        if trade == None:
            return False
        if trade.qty == 0:
            TradeManager.disable_trade(trade, 'InvalidQuantity')
            return False

        now = datetime.now()
        if now > self.stop_timestamp:
            TradeManager.disable_trade(trade, 'NoNewTradesCutOffTimeReached')
            return False

        num_of_trades_placed = TradeManager.get_number_of_trades_placed_by_strategy(self.get_name())
        if num_of_trades_placed >= self.max_trades_per_day:
            TradeManager.disable_trade(trade, 'MaxTradesPerDayReached')
            return False

        return True

    def add_trade_to_list(self, trade):
        if trade != None:
            self.trades.append(trade)

    def get_quote(self, trading_symbol):
        return Quotes.get_quote(trading_symbol, self.is_fno)

    def get_trailing_sl(self, trade):
        return 0