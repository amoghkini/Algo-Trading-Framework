import logging
import threading
import time

from broker.brokers import Brokers
from core.controller import Controller
from exceptions.broker_exceptions import BrokerNotFoundError
from instruments.instruments import Instruments
from strategies.options_bnf_orb_30_min import BNFORB30Min
from strategies.option_selling import OptionSelling
from strategies.sample_strategy import SampleStrategy
from strategies.short_straddle_BNF import ShortStraddleBNF
from ticker.zerodha_ticker import ZerodhaTicker
from trading_engine.trade_manager import TradeManager

Controller.get_broker_login()

class Algo:
    is_algo_running = None

    @staticmethod
    def start_algo():
        if Algo.is_algo_running == True:
            logging.info("Algo has already started..")
            return

        broker_name = Controller.get_broker_name()
        if not broker_name:
            raise BrokerNotFoundError("Broker is not logged in. Hence not able to start the ticker service")      
          
        logging.info("Starting Algo...")
        Instruments.fetch_instruments()

        # start trade manager in a separate thread
        tm = threading.Thread(target=TradeManager.run)
        tm.start()

        # sleep for 2 seconds for TradeManager to get initialized
        time.sleep(2)

        # start running strategies: Run each strategy in a separate thread
        threading.Thread(target=SampleStrategy.get_instance().run).start()
        threading.Thread(target=BNFORB30Min.get_instance().run).start()
        threading.Thread(target=OptionSelling.get_instance().run).start()
        threading.Thread(target=ShortStraddleBNF.get_instance().run).start()

        Algo.is_algo_running = True
        # Write the algo status in new table
        logging.info("Algo started.")


    @staticmethod
    def stop_algo():
        if Algo.is_algo_running == False:
            logging.info("Algo has already stopped...")

        logging.info("Stopping Algo...")

        ticker = Controller.get_broker_login().get_ticker_service_handle()
        if ticker:
            logging.info("The ticker service is running...Going to stop the service")
            ticker.stop_ticker()

        Algo.is_algo_running = False
        # Write the algo status in new table
        logging.info("Algo stopped.")
