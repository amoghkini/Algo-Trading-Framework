import logging
import time

from core.controller import Controller
from ticker.zerodha_ticker import ZerodhaTicker
from order_management_system.zerodha_order_manager import ZerodhaOrderManager
from core.quotes import Quotes
from utils.utils import Utils

class Test:
  def testTicker():
    ticker = ZerodhaTicker()
    ticker.start_ticker()
    ticker.register_listener(Test.tickerListener)

    # sleep for 5 seconds and register trading symbols to receive ticks
    time.sleep(5)
    ticker.register_symbols(['SBIN', 'RELIANCE'])

    # wait for 60 seconds and stop ticker service
    time.sleep(60)
    logging.info('Going to stop ticker')
    ticker.stop_ticker()

  def tickerListener(tick):
    logging.info('tickerLister: onNewTick %s', vars(tick));

  def testOrders():
    order_manager = ZerodhaOrderManager()
    exchange = 'NSE';
    trading_symbol = 'SBIN'
    last_traded_price = Quotes.get_cmp(exchange + ':' + trading_symbol)
    logging.info(trading_symbol + ' CMP = %f', last_traded_price)

    limit_price = last_traded_price - last_traded_price * 1 / 100
    limit_price = Utils.round_to_nse_price(limit_price)
    qty = 1
    direction = 'LONG'

    # place order
    orig_order_id = order_manager.place_order(trading_symbol, limit_price, qty, direction)
    logging.info('Original order Id %s', orig_order_id)

    # sleep for 10 seconds then modify order
    time.sleep(10)
    new_price = last_traded_price
    if orig_order_id:
        order_manager.modify_order(orig_order_id, new_price)

    # sleep for 10 seconds and then place SL order
    time.sleep(10)
    sl_price = new_price - new_price * 1 / 100
    sl_price = Utils.round_to_nse_price(sl_price)
    sl_direction = 'SHORT' if direction == 'LONG' else 'LONG'
    sl_order_id = order_manager.place_sl_order(trading_symbol, sl_price, qty, sl_direction)
    logging.info('SL order Id %s', sl_order_id)

    # sleep for 10 seconds and then place target order
    time.sleep(10)
    target_price = new_price + new_price * 2 / 100
    target_price = Utils.round_to_nse_price(target_price)
    target_direction = 'SHORT' if direction == 'LONG' else 'LONG'
    target_order_id = order_manager.place_order(trading_symbol, target_price, qty, target_direction)
    logging.info('Target order Id %s', target_order_id)

    # sleep for 10 seconds and cancel target order
    time.sleep(10)
    if target_order_id:
        order_manager.cancel_order(target_order_id)
        logging.info('Cancelled Target order Id %s', target_order_id)

    logging.info("Algo done executing all orders. Check ur orders and positions in broker terminal.") 