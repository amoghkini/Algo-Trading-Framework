import os
import logging
import time
import json

from config.config import get_server_config
from core.controller import Controller
from models.direction import Direction
from models.order_status import OrderStatus
from models.order_type import OrderType
from order_management_system.order import Order
from order_management_system.order_input_params import OrderInputParams
from order_management_system.order_modify_params import OrderModifyParams
from order_management_system.zerodha_order_manager import ZerodhaOrderManager
from ticker.zerodha_ticker import ZerodhaTicker
from trading_engine.trade import Trade
from trading_engine.trade_encoder import TradeEncoder
from trading_engine.trade_exit_reason import TradeExitReason
from trading_engine.trade_state import TradeState
from utils.utils import Utils


class TradeManager:
    ticker = None
    trades = [] # to store all the trades
    strategy_to_instance_map = {}
    symbol_to_cmp_map = {}
    intraday_trades_dir = None
    registered_symbols = []

    @staticmethod
    def run():
        if Utils.is_today_holiday():
            logging.info("Cannot start TradeManager as Today is Trading Holiday.")
            return

        if Utils.is_market_closed_for_the_day():
            logging.info("Cannot start TradeManager as Market is closed for the day.")
            return

        Utils.wait_till_market_opens("TradeManager")

        # check and create trades directory for today`s date
        server_config = get_server_config()
        trades_dir = os.path.join(server_config['deployDir'], 'trades')
        TradeManager.intraday_trades_dir = os.path.join(trades_dir, Utils.get_today_date_str())
        if os.path.exists(TradeManager.intraday_trades_dir) == False:
            logging.info('TradeManager: Intraday Trades Directory %s does not exist. Hence going to create.', TradeManager.intraday_trades_dir)
            os.makedirs(TradeManager.intraday_trades_dir)

        # start ticker service
        broker_name = Controller.get_broker_name()
        if broker_name == "Zerodha":
            TradeManager.ticker = ZerodhaTicker()
        # elif broker_name == "fyers" # not implemented
        #   ticker = FyersTicker()

        Controller.get_broker_login().set_ticker_service_handle(TradeManager.ticker)
        
        TradeManager.ticker.start_ticker()
        TradeManager.ticker.register_listener(TradeManager.ticker_listener)

        # sleep for 2 seconds for ticker connection establishment
        time.sleep(2)

        # Load all trades from json files to app memory
        TradeManager.load_all_trades_from_file()

        # track and update trades in a loop
        while True:
            if Utils.is_market_closed_for_the_day():
                logging.info('TradeManager: Stopping TradeManager as market closed.')
                break

            try:
                # Fetch all order details from broker and update orders in each trade
                TradeManager.fetch_and_update_all_trade_orders()
                # track each trade and take necessary action
                TradeManager.track_and_update_all_trades()
            except Exception as e:
                logging.exception("Exception in TradeManager Main thread")

            # save updated data to json file
            TradeManager.save_all_trade_to_file()
            
            # sleep for 30 seconds and then continue
            time.sleep(5)
            logging.info('TradeManager: Main thread woke up..')

    @staticmethod
    def register_strategy(strategy_instance):
        TradeManager.strategy_to_instance_map[strategy_instance.get_name()] = strategy_instance

    @staticmethod
    def load_all_trades_from_file():
        trades_filepath = os.path.join(TradeManager.intraday_trades_dir, 'trades.json')
        if os.path.exists(trades_filepath) == False:
            logging.warn('TradeManager: load_all_trades_from_file() Trades Filepath %s does not exist', trades_filepath)
            return
        TradeManager.trades = []
        t_file = open(trades_filepath, 'r')
        trades_data = json.loads(t_file.read())
        for tr in trades_data:
            trade = TradeManager.convert_json_to_trade(tr)
            logging.info('load_all_trades_from_file trade => %s', trade)
            TradeManager.trades.append(trade)
            if trade.trading_symbol not in TradeManager.registered_symbols:
                # Algo register symbols with ticker
                TradeManager.ticker.register_symbols([trade.trading_symbol])
                TradeManager.registered_symbols.append(trade.trading_symbol)
        logging.info('TradeManager: Successfully loaded %d trades from json file %s', len(TradeManager.trades), trades_filepath)

    @staticmethod
    def save_all_trade_to_file():
        trades_filepath = os.path.join(TradeManager.intraday_trades_dir, 'trades.json')
        with open(trades_filepath, 'w') as t_file:
            json.dump(TradeManager.trades, t_file, indent=2, cls=TradeEncoder)
        logging.info('TradeManager: Saved %d trades to file %s', len(TradeManager.trades), trades_filepath)

    @staticmethod
    def add_new_trade(trade):
        if trade == None:
            return
        logging.info('TradeManager: add_new_trade called for %s', trade)
        for tr in TradeManager.trades:
            if tr.equals(trade):
                logging.warn('TradeManager: Trade already exists so not adding again. %s', trade)
                return
        # Add the new trade to the list
        TradeManager.trades.append(trade)
        logging.info('TradeManager: trade %s added successfully to the list', trade.trade_id)
        # Register the symbol with ticker so that we will start getting ticks for this symbol
        if trade.trading_symbol not in TradeManager.registered_symbols:
            TradeManager.ticker.register_symbols([trade.trading_symbol])
            TradeManager.registered_symbols.append(trade.trading_symbol)
        # Also add the trade to strategy trades list
        strategy_instance = TradeManager.strategy_to_instance_map[trade.strategy]
        if strategy_instance != None:
            strategy_instance.add_trade_to_list(trade)

    @staticmethod
    def disable_trade(trade, reason):
        if trade != None:
            logging.info('TradeManager: Going to disable trade ID %s with the reason %s', trade.trade_id, reason)
            trade.trade_state = TradeState.DISABLED

    @staticmethod
    def ticker_listener(tick):
        # logging.info('tickerLister: new tick received for %s = %f', tick.trading_symbol, tick.lastTradedPrice);
        # Store the latest tick in map
        TradeManager.symbol_to_cmp_map[tick.trading_symbol] = tick.last_traded_price
        # On each new tick, get a created trade and call its strategy whether to place trade or not
        for strategy in TradeManager.strategy_to_instance_map:
            long_trade = TradeManager.get_untriggered_trade(tick.trading_symbol, strategy, Direction.LONG)
            short_trade = TradeManager.get_untriggered_trade(tick.trading_symbol, strategy, Direction.SHORT)
            if long_trade == None and short_trade == None:
                continue
            strategy_instance = TradeManager.strategy_to_instance_map[strategy]
            if long_trade != None:
                if strategy_instance.should_place_trade(long_trade, tick):
                    # place the longTrade
                    is_success = TradeManager.execute_trade(long_trade)
                    if is_success == True:
                        # set longTrade state to ACTIVE
                        long_trade.trade_state = TradeState.ACTIVE
                        long_trade.start_timestamp = Utils.get_epoch()
                        continue
            
            if short_trade != None:
                if strategy_instance.should_place_trade(short_trade, tick):
                    # place the shortTrade
                    is_success = TradeManager.execute_trade(short_trade)
                    if is_success == True:
                        # set shortTrade state to ACTIVE
                        short_trade.trade_state = TradeState.ACTIVE
                        short_trade.start_timestamp = Utils.get_epoch()
    
    @staticmethod
    def get_untriggered_trade(trading_symbol, strategy, direction):
        trade = None
        for tr in TradeManager.trades:
            if tr.trade_state == TradeState.DISABLED:
                continue
            if tr.trade_state != TradeState.CREATED:
                continue
            if tr.trading_symbol != trading_symbol:
                continue
            if tr.strategy != strategy:
                continue
            if tr.direction != direction:
                continue
            trade = tr
            break
        return trade

    @staticmethod
    def execute_trade(trade):
        logging.info('TradeManager: Execute trade called for %s', trade)
        trade.initial_stop_loss = trade.stop_loss
        # Create order input params object and place order
        oip = OrderInputParams(trade.trading_symbol)
        oip.direction = trade.direction
        oip.product_type = trade.product_type
        oip.order_type = OrderType.MARKET if trade.place_market_order == True else OrderType.LIMIT
        oip.price = trade.requested_entry
        oip.qty = trade.qty
        if trade.is_futures == True or trade.is_options == True:
            oip.is_fno = True
        try:
            trade.entry_order = TradeManager.get_order_manager().place_order(oip)
        except Exception as e:
            logging.error('TradeManager: Execute trade failed for tradeID %s: Error => %s', trade.trade_id, str(e))
            return False

        logging.info('TradeManager: Execute trade successful for %s and entry_order %s', trade, trade.entry_order)
        return True

    @staticmethod
    def fetch_and_update_all_trade_orders():
        all_orders = []
        for trade in TradeManager.trades:
            if trade.entry_order != None:
                all_orders.append(trade.entry_order)
            if trade.sl_order != None:
                all_orders.append(trade.sl_order)
            if trade.target_order != None:
                all_orders.append(trade.target_order)

        TradeManager.get_order_manager().fetch_and_update_all_order_details(all_orders)

    @staticmethod
    def track_and_update_all_trades():
        for trade in TradeManager.trades:
            if trade.trade_state == TradeState.ACTIVE:
                if trade.intraday_square_off_timestamp != None:
                    nowEpoch = Utils.get_epoch()
                    if nowEpoch >= trade.intraday_square_off_timestamp:
                        TradeManager.square_off_trade(trade, TradeExitReason.SQUARE_OFF)
                
                TradeManager.track_entry_order(trade)
                TradeManager.track_sl_order(trade)
                TradeManager.track_target_order(trade)

    @staticmethod
    def track_entry_order(trade):
        if trade.trade_state != TradeState.ACTIVE:
            return

        if trade.entry_order == None:
            return

        if trade.entry_order.order_status == OrderStatus.CANCELLED or trade.entry_order.order_status == OrderStatus.REJECTED:
            trade.trade_state = TradeState.CANCELLED

        trade.filled_qty = trade.entry_order.filled_qty
        if trade.filled_qty > 0:
            trade.entry = trade.entry_order.average_price
        # Update the current market price and calculate pnl
        trade.cmp = TradeManager.symbol_to_cmp_map[trade.trading_symbol]
        Utils.calculate_trade_pnl(trade)

    @staticmethod
    def track_sl_order(trade):
        if trade.trade_state != TradeState.ACTIVE:
            return
        if trade.stop_loss == 0: # Do not place SL order if no stoploss provided
            return
        if trade.sl_order == None:
            # Place SL order
            TradeManager.place_sl_order(trade)
        else:
            if trade.sl_order.order_status == OrderStatus.COMPLETE:
                # SL Hit
                exit = trade.sl_order.average_price
                exit_reason = TradeExitReason.SL_HIT if trade.initial_stop_loss == trade.stop_loss else TradeExitReason.TRAIL_SL_HIT
                TradeManager.set_trade_to_completed(trade, exit, exit_reason)
                # Make sure to cancel target order if exists
                TradeManager.cancel_target_order(trade)

            elif trade.sl_order.order_status == OrderStatus.CANCELLED:
                # SL order cancelled outside of algo (manually or by broker or by exchange)
                logging.error('SL order %s for tradeID %s cancelled outside of Algo. Setting the trade as completed with exit price as current market price.', trade.sl_order.order_id, trade.trade_id)
                exit = TradeManager.symbol_to_cmp_map[trade.trading_symbol]
                TradeManager.set_trade_to_completed(trade, exit, TradeExitReason.SL_CANCELLED)
                # Cancel target order if exists
                TradeManager.cancel_target_order(trade)

            else:
                TradeManager.check_and_update_trail_sl(trade)

    @staticmethod
    def check_and_update_trail_sl(trade):
        # Trail the SL if applicable for the trade
        strategy_instance = TradeManager.strategy_to_instance_map[trade.strategy]
        if strategy_instance == None:
            return

        new_trail_sl = strategy_instance.get_trailing_sl(trade)
        update_sl = False
        if new_trail_sl > 0:
            if trade.direction == Direction.LONG and new_trail_sl > trade.stop_loss:
                update_sl = True
            elif trade.direction == Direction.SHORT and new_trail_sl < trade.stop_loss:
                update_sl = True
        if update_sl == True:
            omp = OrderModifyParams()
            omp.new_trigger_price = new_trail_sl
            try:
                old_sl = trade.stop_loss
                TradeManager.get_order_manager().modify_order(trade.sl_order, omp)
                logging.info('TradeManager: Trail SL: Successfully modified stopLoss from %f to %f for tradeID %s', old_sl, new_trail_sl, trade.trade_id)
                trade.stop_loss = new_trail_sl # IMPORTANT: Dont forget to update this on successful modification
            except Exception as e:
                logging.error('TradeManager: Failed to modify SL order for tradeID %s orderId %s: Error => %s', trade.trade_id, trade.sl_order.order_id, str(e))

    @staticmethod
    def track_target_order(trade):
        if trade.trade_state != TradeState.ACTIVE:
            return
        if trade.target == 0: # Do not place Target order if no target provided
            return
        if trade.target_order == None:
            # Place Target order
            TradeManager.place_target_order(trade)
        else:
            if trade.target_order.order_status == OrderStatus.COMPLETE:
                # Target Hit
                exit = trade.target_order.average_price
                TradeManager.set_trade_to_completed(trade, exit, TradeExitReason.TARGET_HIT)
                # Make sure to cancel sl order
                TradeManager.cancel_sl_order(trade)

            elif trade.target_order.order_status == OrderStatus.CANCELLED:
                # Target order cancelled outside of algo (manually or by broker or by exchange)
                logging.error('Target order %s for trade_id %s cancelled outside of Algo. Setting the trade as completed with exit price as current market price.', trade.target_order.order_id, trade.trade_id)
                exit = TradeManager.symbol_to_cmp_map[trade.trading_symbol]
                TradeManager.set_trade_to_completed(trade, exit, TradeExitReason.TARGET_CANCELLED)
                # Cancel SL order
                TradeManager.cancel_sl_order(trade)

    @staticmethod
    def place_sl_order(trade):
        oip = OrderInputParams(trade.trading_symbol)
        oip.direction = Direction.SHORT if trade.direction == Direction.LONG else Direction.LONG 
        oip.product_type = trade.product_type
        oip.order_type = OrderType.SL_MARKET
        oip.trigger_price = trade.stop_loss
        oip.qty = trade.qty
        if trade.is_futures == True or trade.is_options == True:
            oip.is_fno = True
        try:
            trade.sl_order = TradeManager.get_order_manager().place_order(oip)
        except Exception as e:
            logging.error('TradeManager: Failed to place SL order for trade_id %s: Error => %s', trade.trade_id, str(e))
            return False
        logging.info('TradeManager: Successfully placed SL order %s for trade_id %s', trade.sl_order.order_id, trade.trade_id)
        return True

    @staticmethod
    def place_target_order(trade, is_market_order=False):
        oip = OrderInputParams(trade.trading_symbol)
        oip.direction = Direction.SHORT if trade.direction == Direction.LONG else Direction.LONG
        oip.product_type = trade.product_type
        oip.order_type = OrderType.MARKET if is_market_order == True else OrderType.LIMIT
        oip.price = 0 if is_market_order == True else trade.target
        oip.qty = trade.qty
        if trade.is_futures == True or trade.is_options == True:
            oip.is_fno = True
        try:
            trade.target_order = TradeManager.get_order_manager().place_order(oip)
        except Exception as e:
            logging.error('TradeManager: Failed to place Target order for trade_id %s: Error => %s', trade.trade_id, str(e))
            return False
        logging.info('TradeManager: Successfully placed Target order %s for trade_id %s', trade.target_order.order_id, trade.trade_id)
        return True

    @staticmethod
    def cancel_entry_order(trade):
        if trade.entry_order == None:
            return
        if trade.entry_order.order_status == OrderStatus.CANCELLED:
            return
        try:
            TradeManager.get_order_manager().cancel_order(trade.entry_order)
        except Exception as e:
            logging.error('TradeManager: Failed to cancel Entry order %s for trade_id %s: Error => %s', trade.entry_order.order_id, trade.trade_id, str(e))
        logging.info('TradeManager: Successfully cancelled Entry order %s for trade_id %s', trade.entry_order.order_id, trade.trade_id)

    @staticmethod
    def cancel_sl_order(trade):
        if trade.sl_order == None:
            return
        if trade.sl_order.order_status == OrderStatus.CANCELLED:
            return
        try:
            TradeManager.get_order_manager().cancel_order(trade.sl_order)
        except Exception as e:
            logging.error('TradeManager: Failed to cancel SL order %s for trade_id %s: Error => %s', trade.sl_order.order_id, trade.trade_id, str(e))
        logging.info('TradeManager: Successfully cancelled SL order %s for trade_id %s', trade.sl_order.order_id, trade.trade_id)

    @staticmethod
    def cancel_target_order(trade):
        if trade.target_order == None:
            return
        if trade.target_order.order_status == OrderStatus.CANCELLED:
            return
        try:
            TradeManager.get_order_manager().cancel_order(trade.target_order)
        except Exception as e:
            logging.error('TradeManager: Failed to cancel Target order %s for trade_id %s: Error => %s', trade.target_order.order_id, trade.trade_id, str(e))
        logging.info('TradeManager: Successfully cancelled Target order %s for trade_id %s', trade.target_order.order_id, trade.trade_id)

    @staticmethod
    def set_trade_to_completed(trade, exit, exit_reason=None):
        trade.tradeState = TradeState.COMPLETED
        trade.exit = exit
        trade.exit_reason = exit_reason if trade.exit_reason == None else trade.exit_reason
        trade.end_timestamp = Utils.get_epoch()
        trade = Utils.calculate_trade_pnl(trade)
        logging.info('TradeManager: set_trade_to_completed strategy = %s, symbol = %s, qty = %d, entry = %f, exit = %f, pnl = %f, exit reason = %s', trade.strategy, trade.trading_symbol, trade.filled_qty, trade.entry, trade.exit, trade.pnl, trade.exit_reason)

    @staticmethod
    def square_off_trade(trade, reason = TradeExitReason.SQUARE_OFF):
        logging.info('TradeManager: square_off_trade called for trade_id %s with reason %s', trade.trade_id, reason)
        if trade == None or trade.trade_state != TradeState.ACTIVE:
            return

        trade.exit_reason = reason
        if trade.entry_order != None:
            if trade.entry_order.order_status == OrderStatus.OPEN:
                # Cancel entry order if it is still open (not filled or partially filled case)
                TradeManager.cancel_entry_order(trade)

        if trade.sl_order != None:
            TradeManager.cancel_sl_order(trade)

        if trade.target_order != None:
            # Change target order type to MARKET to exit position immediately
            logging.info('TradeManager: changing target order %s to MARKET to exit position for tradeID %s', trade.target_order.order_id, trade.trade_id)
            TradeManager.get_order_manager().modify_order_to_market(trade.target_order)
        else:
            # Place new target order to exit position
            logging.info('TradeManager: placing new target order to exit position for tradeID %s', trade.trade_id)
            TradeManager.place_target_order(trade, True)

    @staticmethod
    def get_order_manager():
        order_manager = None
        broker_name = Controller.get_broker_name()
        if broker_name == "Zerodha":
            order_manager = ZerodhaOrderManager()
        # elif broker_name == "fyers": # Not implemented
        return order_manager

    @staticmethod
    def get_number_of_trades_placed_by_strategy(strategy):
        count = 0
        for trade in TradeManager.trades:
            if trade.strategy != strategy:
                continue
            if trade.trade_state == TradeState.CREATED or trade.trade_state == TradeState.DISABLED:
                continue
            # consider active/completed/cancelled trades as trades placed
            count += 1
        return count

    @staticmethod
    def get_all_trades_by_strategy(strategy):
        trades_by_strategy = []
        for trade in TradeManager.trades:
            if trade.strategy == strategy:
                trades_by_strategy.append(trade)
        return trades_by_strategy

    @staticmethod
    def convert_json_to_trade(json_data):
        trade = Trade(json_data['trading_symbol'])
        trade.trade_id = json_data['trade_id']
        trade.strategy = json_data['strategy']
        trade.direction = json_data['direction']
        trade.product_type = json_data['product_type']
        trade.is_futures = json_data['is_futures']
        trade.is_options = json_data['is_options']
        trade.option_type = json_data['option_type']
        trade.place_market_order = json_data['place_market_order']
        trade.intraday_square_off_timestamp = json_data['intraday_square_off_timestamp']
        trade.requested_entry = json_data['requested_entry']
        trade.entry = json_data['entry']
        trade.qty = json_data['qty']
        trade.filled_qty = json_data['filled_qty']
        trade.initial_stop_loss = json_data['initial_stop_loss']
        trade.stop_loss = json_data['stop_loss']
        trade.target = json_data['target']
        trade.cmp = json_data['cmp']
        trade.trade_state = json_data['trade_state']
        trade.timestamp = json_data['timestamp']
        trade.create_timestamp = json_data['create_timestamp']
        trade.start_timestamp = json_data['start_timestamp']
        trade.end_timestamp = json_data['end_timestamp']
        trade.pnl = json_data['pnl']
        trade.pnl_percentage = json_data['pnl_percentage']
        trade.exit = json_data['exit']
        trade.exit_reason = json_data['exit_reason']
        trade.exchange = json_data['exchange']
        trade.entry_order = TradeManager.convert_json_to_order(json_data['entry_order'])
        trade.sl_order = TradeManager.convert_json_to_order(json_data['sl_order'])
        trade.target_order = TradeManager.convert_json_to_order(json_data['target_order'])
        return trade

    @staticmethod
    def convert_json_to_order(json_data):
        if json_data == None:
            return None
        order = Order()
        order.trading_symbol = json_data['trading_symbol']
        order.exchange = json_data['exchange']
        order.product_type = json_data['product_type']
        order.order_type = json_data['order_type']
        order.price = json_data['price']
        order.trigger_price = json_data['trigger_price']
        order.qty = json_data['qty']
        order.order_id = json_data['order_id']
        order.order_status = json_data['order_status']
        order.average_price = json_data['average_price']
        order.filled_qty = json_data['filled_qty']
        order.pending_qty = json_data['pending_qty']
        order.order_place_timestamp = json_data['order_place_timestamp']
        order.last_order_update_timestamp = json_data['last_order_update_timestamp']
        order.message = json_data['message']
        return order

    @staticmethod
    def get_last_traded_price(trading_symbol):
        return TradeManager.symbol_to_cmp_map[trading_symbol]
