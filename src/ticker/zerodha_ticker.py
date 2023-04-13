import logging
import json
from kiteconnect import KiteTicker

from instruments.instruments import Instruments
from models.tick_data import TickData
from ticker.base_ticker import BaseTicker

class ZerodhaTicker(BaseTicker):
    def __init__(self):
        super().__init__("zerodha")

    def start_ticker(self):
        broker_app_details = self.broker_login.get_broker_app_details()
        access_token = self.broker_login.get_access_token()
        if access_token == None:
            logging.error('ZerodhaTicker start_ticker: Cannot start ticker as access_token is empty')
            return
        
        ticker = KiteTicker(broker_app_details.app_key, access_token)
        ticker.on_connect = self.on_connect
        ticker.on_close = self.on_close
        ticker.on_error = self.on_error
        ticker.on_reconnect = self.on_reconnect
        ticker.on_noreconnect = self.on_noreconnect
        ticker.on_ticks = self.on_ticks
        ticker.on_order_update = self.on_order_update

        logging.info('ZerodhaTicker: Going to connect..')
        self.ticker = ticker
        self.ticker.connect(threaded=True)

    def stop_ticker(self):
        logging.info('ZerodhaTicker: stopping..')
        self.ticker.close(1000, "Manual close")

    def register_symbols(self, symbols):
        tokens = []
        for symbol in symbols:
            isd = Instruments.get_instrument_data_by_symbol(symbol)
            token = isd['instrument_token']
            logging.info('ZerodhaTicker register_symbols: %s token = %s', symbol, token)
            tokens.append(token)

        logging.info('ZerodhaTicker Subscribing tokens %s', tokens)
        self.ticker.subscribe(tokens)

    def unregister_symbols(self, symbols):
        tokens = []
        for symbol in symbols:
            isd = Instruments.get_instrument_data_by_symbol(symbol)
            token = isd['instrument_token']
            logging.info('ZerodhaTicker unregister_symbols: %s token = %s', symbol, token)
            tokens.append(token)

        logging.info('ZerodhaTicker Unsubscribing tokens %s', tokens)
        self.ticker.unsubscribe(tokens)

    def on_ticks(self, ws, broker_ticks):
      # convert broker specific Ticks to our system specific Ticks (models.TickData) and pass to super class function
      ticks = []
      for b_tick in broker_ticks:
          isd = Instruments.get_instrument_data_by_token(b_tick['instrument_token'])
          trading_symbol = isd['tradingsymbol']
          tick = TickData(trading_symbol)
          tick.last_traded_price = b_tick['last_price']
          tick.last_traded_quantity = b_tick['last_traded_quantity']
          tick.avg_traded_price = b_tick['average_traded_price']
          tick.volume = b_tick['volume_traded']
          tick.total_buy_quantity = b_tick['total_buy_quantity']
          tick.total_sell_quantity = b_tick['total_sell_quantity']
          tick.open = b_tick['ohlc']['open']
          tick.high = b_tick['ohlc']['high']
          tick.low = b_tick['ohlc']['low']
          tick.close = b_tick['ohlc']['close']
          tick.change = b_tick['change']
          ticks.append(tick)
        
      self.on_new_ticks(ticks)

    def on_connect(self, ws, response):
        self.onConnect()

    def on_close(self, ws, code, reason):
        self.onDisconnect(code, reason)

    def on_error(self, ws, code, reason):
        self.onError(code, reason)

    def on_reconnect(self, ws, attemptsCount):
        self.onReconnect(attemptsCount)

    def on_noreconnect(self, ws):
        self.onMaxReconnectsAttempt()

    def on_order_update(self, ws, data):
        self.onOrderUpdate(data)
