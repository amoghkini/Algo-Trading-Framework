import logging

from models.direction import Direction
from models.order_status import OrderStatus
from models.order_type import OrderType
from models.product_type import ProductType
from order_management_system.base_order_manager import BaseOrderManager
from order_management_system.order import Order
from utils.utils import Utils

class ZerodhaOrderManager(BaseOrderManager):
    def __init__(self):
        super().__init__("zerodha")

    def place_order(self, order_input_params):
        logging.info('%s: Going to place order with params %s', self.broker, order_input_params)
        kite = self.broker_handle
        try:
            order_id = kite.place_order(
              variety=kite.VARIETY_REGULAR,
              exchange=kite.EXCHANGE_NFO if order_input_params.is_fno == True else kite.EXCHANGE_NSE,
              tradingsymbol=order_input_params.trading_symbol,
              transaction_type=self.convert_to_broker_direction(order_input_params.direction),
              quantity=order_input_params.qty,
              price=order_input_params.price,
              trigger_price=order_input_params.trigger_price,
              product=self.convert_to_broker_product_type(order_input_params.product_type),
              order_type=self.convert_to_broker_order_type(order_input_params.order_type))

            logging.info('%s: Order placed successfully, orderId = %s', self.broker, order_id)
            order = Order(order_input_params)
            order.order_id = order_id
            order.order_place_timestamp = Utils.get_epoch()
            order.last_order_update_timestamp = Utils.get_epoch()
            return order
        except Exception as e:
            logging.info('%s Order placement failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def modify_order(self, order, order_modify_params):
        logging.info('%s: Going to modify order with params %s', self.broker, order_modify_params)
        kite = self.broker_handle
        try:
            order_id = kite.modify_order(
              variety=kite.VARIETY_REGULAR,
              order_id=order.order_id,
              quantity=order_modify_params.new_qty if order_modify_params.new_qty > 0 else None,
              price=order_modify_params.new_price if order_modify_params.new_price > 0 else None,
              trigger_price=order_modify_params.new_trigger_price if order_modify_params.new_trigger_price > 0 else None,
              order_type=order_modify_params.new_order_type if order_modify_params.new_order_type != None else None)

            logging.info('%s Order modified successfully for order_id = %s', self.broker, order_id)
            order.last_order_update_timestamp = Utils.get_epoch()
            return order
        
        except Exception as e:
            logging.info('%s Order modify failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def modify_order_to_market(self, order):
        logging.info('%s: Going to modify order with params %s', self.broker)
        kite = self.broker_handle
        try:
            order_id = kite.modify_order(
              variety=kite.VARIETY_REGULAR,
              order_id=order.order_id,
              order_type=kite.ORDER_TYPE_MARKET)

            logging.info('%s Order modified successfully to MARKET for order_id = %s', self.broker, order_id)
            order.last_order_update_timestamp = Utils.get_epoch()
            return order
        except Exception as e:
            logging.info('%s Order modify to market failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def cancel_order(self, order):
        logging.info('%s Going to cancel order %s', self.broker, order.order_id)
        kite = self.broker_handle
        try:
            order_id = kite.cancel_order(
              variety=kite.VARIETY_REGULAR,
              order_id=order.order_id)

            logging.info('%s Order cancelled successfully, order_id = %s', self.broker, order_id)
            order.last_order_update_timestamp = Utils.get_epoch()
            return order
        except Exception as e:
            logging.info('%s Order cancel failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def fetch_and_update_all_order_details(self, orders):
        logging.info('%s Going to fetch order book', self.broker)
        kite = self.broker_handle
        order_book = None
        try:
            order_book = kite.orders()
        except Exception as e:
            logging.error('%s Failed to fetch order book', self.broker)
            return

        logging.info('%s Order book length = %d', self.broker, len(order_book))
        num_orders_updated = 0
        for b_order in order_book:
            found_order = None
            for order in orders:
                if order.order_id == b_order['order_id']:
                    found_order = order
                    break
            
            if found_order != None:
                logging.info('Found order for order_id %s', found_order.order_id)
                found_order.qty = b_order['quantity']
                found_order.filled_qty = b_order['filled_quantity']
                found_order.pending_qty = b_order['pending_quantity']
                found_order.order_status = b_order['status']
                if found_order.order_status == OrderStatus.CANCELLED and found_order.filled_qty > 0:
                    # Consider this case as completed in our system as we cancel the order with pending qty when strategy stop timestamp reaches
                    found_order.order_status = OrderStatus.COMPLETED
                found_order.price = b_order['price']
                found_order.trigger_price = b_order['trigger_price']
                found_order.average_price = b_order['average_price']
                logging.info('%s Updated order %s', self.broker, found_order)
                num_orders_updated += 1

        logging.info('%s: %d orders updated with broker order details', self.broker, num_orders_updated)

    def convert_to_broker_product_type(self, product_type):
        kite = self.broker_handle
        if product_type == ProductType.MIS:
            return kite.PRODUCT_MIS
        elif product_type == ProductType.NRML:
            return kite.PRODUCT_NRML
        elif product_type == ProductType.CNC:
            return kite.PRODUCT_CNC
        return None 

    def convert_to_broker_order_type(self, order_type):
        kite = self.broker_handle
        if order_type == OrderType.LIMIT:
            return kite.ORDER_TYPE_LIMIT
        elif order_type == OrderType.MARKET:
            return kite.ORDER_TYPE_MARKET
        elif order_type == OrderType.SL_MARKET:
            return kite.ORDER_TYPE_SLM
        elif order_type == OrderType.SL_LIMIT:
            return kite.ORDER_TYPE_SL
        return None

    def convert_to_broker_direction(self, direction):
        kite = self.broker_handle
        if direction == Direction.LONG:
            return kite.TRANSACTION_TYPE_BUY
        elif direction == Direction.SHORT:
            return kite.TRANSACTION_TYPE_SELL
        return None
