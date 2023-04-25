from core.controller import Controller
from models.quote import Quote

class Quotes:
    @staticmethod
    def get_quote(trading_symbol, is_fno = False):
        broker = Controller.get_broker_name()
        broker_handle = Controller.get_broker_login().get_broker_handle()
        quote = None
        if broker == "Zerodha":
            key = ('NFO:' + trading_symbol) if is_fno == True else ('NSE:' + trading_symbol)
            b_quote_resp = broker_handle.quote(key)
            b_quote = b_quote_resp[key]
            # convert broker quote to our system quote
            quote = Quote(trading_symbol)
            quote.trading_symbol = trading_symbol
            quote.last_traded_price = b_quote['last_price']
            quote.last_traded_quantity = b_quote['last_quantity']
            quote.avg_traded_price = b_quote['average_price']
            quote.volume = b_quote['volume']
            quote.total_buy_quantity = b_quote['buy_quantity']
            quote.total_sell_quantity = b_quote['sell_quantity']
            ohlc = b_quote['ohlc']
            quote.open = ohlc['open']
            quote.high = ohlc['high']
            quote.low = ohlc['low']
            quote.close = ohlc['close']
            quote.change = b_quote['net_change']
            quote.oi_day_high = b_quote['oi_day_high']
            quote.oi_day_low = b_quote['oi_day_low']
            quote.lower_circuit_limit = b_quote['lower_circuit_limit']
            quote.upper_circuit_limit = b_quote['upper_circuit_limit']
            # Add code to store the market depth
        else:
            # The logic may be different for other brokers
            quote = None
        return quote

    @staticmethod
    def get_cmp(trading_symbol):
        quote = Quotes.get_quote(trading_symbol)
        if quote:
            return quote.last_traded_price
        else:
            return 0
