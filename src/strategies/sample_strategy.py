import logging

from models.direction import Direction
from models.product_type import ProductType
from strategies.base_strategy import BaseStrategy
from trademgmt.trade import Trade
from trademgmt.trade_manager import TradeManager
from utils.utils import Utils

# Each strategy has to be derived from BaseStrategy
class SampleStrategy(BaseStrategy):
    __instance = None

    @staticmethod
    def get_instance(): # singleton class
        if SampleStrategy.__instance == None:
            SampleStrategy()
        return SampleStrategy.__instance

    def __init__(self):
        if SampleStrategy.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SampleStrategy.__instance = self
        # Call Base class constructor
        super().__init__("SAMPLE")
        # Initialize all the properties specific to this strategy
        self.product_type = ProductType.MIS
        self.symbols = ["SBIN", "INFY", "TATASTEEL", "RELIANCE", "HDFCBANK", "CIPLA"]
        self.sl_percentage = 1.1
        self.target_percentage = 2.2
        self.start_timestamp = Utils.get_time_of_today(9, 30, 0) # When to start the strategy. Default is Market start time
        self.stop_timestamp = Utils.get_time_of_today(14, 30, 0) # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = Utils.get_time_of_today(15, 0, 0) # Square off time
        self.capital = 3000 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 2 # 2x, 3x Etc
        self.max_trades_per_day = 3  # Max number of trades per day under this strategy
        self.is_fno = False  # Does this strategy trade in FnO or not
        self.capital_per_set = 0 # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)

    def process(self):
        if len(self.trades) >= self.max_trades_per_day:
            return
        # This is a sample strategy with the following logic:
        # 1. If current market price > 0.5% from previous day close then create LONG trade
        # 2. If current market price < 0.5% from previous day close then create SHORT trade
        for symbol in self.symbols:
            quote = self.get_quote(symbol)
            if quote == None:
                logging.error('%s: Could not get quote for %s', self.get_name(), symbol)
                continue
            long_breakout_price = Utils.round_to_nse_price(quote.close + quote.close * 0.5 / 100)
            short_breakout_price = Utils.round_to_nse_price(quote.close - quote.close * 0.5 / 100)
            cmp = quote.last_traded_price
            logging.info('%s: %s => long = %f, short = %f, CMP = %f', self.get_name(), symbol, long_breakout_price, short_breakout_price, cmp)
            
            direction = None
            breakout_price = 0
            if cmp > long_breakout_price:
                direction = 'LONG'
                breakout_price = long_breakout_price
            elif cmp < short_breakout_price:
                direction = 'SHORT'
                breakout_price = short_breakout_price
            if direction == None:
                continue

            self.generate_trade(symbol, direction, breakout_price, cmp)

    def generate_trade(self, trading_symbol, direction, breakout_price, cmp):
        trade = Trade(trading_symbol)
        trade.strategy = self.get_name()
        trade.direction = direction
        trade.product_type = self.product_type
        trade.place_market_order = True
        trade.requested_entry = breakout_price
        trade.timestamp = Utils.get_epoch(self.start_timestamp) # setting this to strategy timestamp
        trade.qty = int(self.calculate_capital_per_trade() / breakout_price)
        if trade.qty == 0:
            trade.qty = 1 # Keep min 1 qty
        if direction == 'LONG':
            trade.stop_loss = Utils.round_to_nse_price(breakout_price - breakout_price * self.sl_percentage / 100)
            if cmp < trade.stop_loss:
                trade.stop_loss = Utils.round_to_nse_price(cmp - cmp * 1 / 100)
        else:
            trade.stop_loss = Utils.round_to_nse_price(breakout_price + breakout_price * self.sl_percentage / 100)
            if cmp > trade.stop_loss:
                trade.stop_loss = Utils.round_to_nse_price(cmp + cmp * 1 / 100)

        if direction == 'LONG':
            trade.target = Utils.round_to_nse_price(breakout_price + breakout_price * self.target_percentage / 100)
        else:
            trade.target = Utils.round_to_nse_price(breakout_price - breakout_price * self.target_percentage / 100)

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
