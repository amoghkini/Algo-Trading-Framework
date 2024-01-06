import logging
from datetime import datetime

from instruments.instruments import Instruments
from models.direction import Direction
from models.product_type import ProductType
from strategies.base_strategy import BaseStrategy
from trading_engine.trade import Trade
from trading_engine.trade_manager import TradeManager
from utils.time_utils import TimeUtils
from utils.utils import Utils

# Each strategy has to be derived from BaseStrategy
class ShortStraddleBNF(BaseStrategy):
    __instance = None

    @staticmethod
    def get_instance():  # singleton class
        if ShortStraddleBNF.__instance == None:
            ShortStraddleBNF()
        return ShortStraddleBNF.__instance

    def __init__(self):
        if ShortStraddleBNF.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ShortStraddleBNF.__instance = self
        # Call Base class constructor
        super().__init__("ShortStraddleBNF")
        # Initialize all the properties specific to this strategy
        self.product_type = ProductType.MIS
        self.symbols = []
        self.sl_percentage = 30
        self.target_percentage = 0
        self.start_timestamp = Utils.get_time_of_today(11, 0, 0) # When to start the strategy. Default is Market start time
        self.stop_timestamp = Utils.get_time_of_today(14, 0, 0) # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = Utils.get_time_of_today(14, 30, 0) # Square off time
        self.capital = 100000 # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 0
        self.max_trades_per_day = 2 # (1 CE + 1 PE) Max number of trades per day under this strategy
        self.is_fno = True  # Does this strategy trade in FnO or not
        self.capital_per_set = 100000 # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)

    def can_trade_today(self):
        # Even if you remove this function can_trade_today() completely its same as allowing trade every day
        return True

    def process(self):
        now = datetime.now()
        if now < self.start_timestamp:
            return
        if len(self.trades) >= self.max_trades_per_day:
            return

        # Get current market price of Nifty Future
        future_symbol = Utils.prepare_monthly_expiry_futures_symbol('BANKNIFTY')
        quote = self.get_quote(future_symbol)
        if quote == None:
            logging.error('%s: Could not get quote for %s', self.get_name(), future_symbol)
            return

        atm_strike = Utils.get_nearest_strike_price(quote.last_traded_price, 100)
        logging.info('%s: Nifty CMP = %f, atm_strike = %d', self.get_name(), quote.last_traded_price, atm_strike)

        atm_ce_symbol = Utils.prepare_weekly_options_symbol("BANKNIFTY", atm_strike, 'CE')
        atm_pe_symbol = Utils.prepare_weekly_options_symbol("BANKNIFTY", atm_strike, 'PE')
        logging.info('%s: atm_ce_symbol = %s, atm_pe_symbol = %s', self.get_name(), atm_ce_symbol, atm_pe_symbol)
        # create trades
        self.generate_trades(atm_ce_symbol, atm_pe_symbol)

    def generate_trades(self, atm_ce_symbol, atm_pe_symbol):
        num_lots = self.calculate_lots_per_trade()
        quote_atm_ce_symbol = self.get_quote(atm_ce_symbol)
        quote_atm_pe_symbol = self.get_quote(atm_pe_symbol)
        if quote_atm_ce_symbol == None or quote_atm_pe_symbol == None:
            logging.error('%s: Could not get quotes for option symbols', self.get_name())
            return

        self.generate_trade(atm_ce_symbol, num_lots, quote_atm_ce_symbol.last_traded_price)
        self.generate_trade(atm_pe_symbol, num_lots, quote_atm_pe_symbol.last_traded_price)
        logging.info('%s: Trades generated.', self.get_name())

    def generate_trade(self, option_symbol, num_lots, last_traded_price):
        trade = Trade(option_symbol)
        trade.strategy = self.get_name()
        trade.is_options = True
        trade.direction = Direction.SHORT # Always short here as option selling only
        trade.product_type = self.product_type
        trade.place_market_order = True
        trade.requested_entry = last_traded_price
        trade.timestamp = TimeUtils.get_epoch(self.start_timestamp) # setting this to strategy timestamp
        
        isd = Instruments.get_instrument_data_by_symbol(option_symbol)  # Get instrument data to know qty per lot
        trade.qty = isd['lot_size'] * num_lots
        
        trade.stop_loss = Utils.round_to_nse_price(trade.requested_entry + trade.requested_entry * self.sl_percentage / 100)
        trade.target = 0 # setting to 0 as no target is applicable for this trade

        trade.intraday_square_off_timestamp = TimeUtils.get_epoch(self.square_off_timestamp)
        # Hand over the trade to TradeManager
        TradeManager.add_new_trade(trade)

    def should_place_trade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if super().should_place_trade(trade, tick) == False:
            return False
        # We dont have any condition to be checked here for this strategy just return True
        return True

    def get_trailing_sl(self, trade):
        if trade == None:
            return 0
        if trade.entry == 0:
            return 0
        last_traded_price = TradeManager.get_last_traded_price(trade.trading_symbol)
        if last_traded_price == 0:
            return 0

        trail_sl = 0
        profit_points = int(trade.entry - last_traded_price)
        if profit_points >= 5:
            factor = int(profit_points / 5)
            trail_sl = Utils.round_to_nse_price(trade.initial_stop_loss - factor * 5)
        logging.info('%s: %s Returning trail SL %f', self.get_name(), trade.trading_symbol, trail_sl)
        return trail_sl

