import os
import logging
import json

from config.config import get_server_config, get_timestamps_data, save_timestamps_data
from core.controller import Controller
from utils.utils import Utils

class Instruments:
    instruments_list = None
    symbol_to_instrument_map = None
    token_to_instrument_map = None

    @staticmethod
    def should_fetch_from_server():
        timestamps = get_timestamps_data()
        if 'instrumentsLastSavedAt' not in timestamps:
            return True
        last_saved_timestamp = timestamps['instrumentsLastSavedAt']
        now_epoch = Utils.get_epoch()
        if now_epoch - last_saved_timestamp >= 24 * 60 * 60:
            logging.info("Instruments: should_fetch_from_server() returning True as its been 24 hours since last fetch.")
            return True
        return False

    @staticmethod
    def update_last_saved_timestamp():
        timestamps = get_timestamps_data()
        timestamps['instrumentsLastSavedAt'] = Utils.get_epoch()
        save_timestamps_data(timestamps)

    @staticmethod
    def load_instruments():
        server_config = get_server_config()
        instruments_file_path = os.path.join(server_config['deployDir'], 'instruments.json')
        if os.path.exists(instruments_file_path) == False:
            logging.warn('Instruments: instruments_file_path %s does not exist', instruments_file_path)
            return [] # returns empty list

        isd_file = open(instruments_file_path, 'r')
        instruments = json.loads(isd_file.read())
        logging.info('Instruments: loaded %d instruments from file %s', len(instruments), instruments_file_path)
        return instruments

    @staticmethod
    def save_instruments(instruments = []):
        server_config = get_server_config()
        instruments_file_path = os.path.join(server_config['deployDir'], 'instruments.json')
        with open(instruments_file_path, 'w') as isd_File:
            json.dump(instruments, isd_File, indent=2, default=str)
        logging.info('Instruments: Saved %d instruments to file %s', len(instruments), instruments_file_path)
        
        # Update last save timestamp
        Instruments.update_last_saved_timestamp()

    @staticmethod
    def fetch_instruments_from_server():
        instruments_list = []
        try:
            broker_handle = Controller.get_broker_login().get_broker_handle()
            logging.info('Going to fetch instruments from server...')
            instruments_list = broker_handle.instruments('NSE')
            instruments_list_fno = broker_handle.instruments('NFO')
            # Add FnO instrument list to the main list
            instruments_list.extend(instruments_list_fno)
            logging.info('Fetched %d instruments from server.', len(instruments_list))
        except Exception as e:
            logging.exception("Exception while fetching instruments from server")
        return instruments_list

    @staticmethod
    def fetch_instruments():
        if Instruments.instruments_list:
            return Instruments.instruments_list

        instruments_list = Instruments.load_instruments()
        if len(instruments_list) == 0 or Instruments.should_fetch_from_server() == True:
            instruments_list = Instruments.fetch_instruments_from_server()
            # Save instruments to file locally
            if len(instruments_list) > 0:
                Instruments.save_instruments(instruments_list)

        if len(instruments_list) == 0:
            print("Could not fetch/load instruments data. Hence exiting the app.")
            logging.error("Could not fetch/load instruments data. Hence exiting the app.");
            exit(-2)
        
        Instruments.symbol_to_instrument_map = {}
        Instruments.token_to_instrument_map = {}
        for isd in instruments_list:
            trading_symbol = isd['tradingsymbol']
            instrument_token = isd['instrument_token']
            # logging.info('%s = %d', tradingSymbol, instrumentToken)
            Instruments.symbol_to_instrument_map[trading_symbol] = isd
            Instruments.token_to_instrument_map[instrument_token] = isd
        
        logging.info('Fetching instruments done. Instruments count = %d', len(instruments_list))
        # assign the list to static variable
        Instruments.instruments_list = instruments_list
        return instruments_list

    @staticmethod
    def get_instrument_data_by_symbol(trading_symbol):
        return Instruments.symbol_to_instrument_map[trading_symbol]

    @staticmethod
    def get_instrument_data_by_token(instrument_token):
        return Instruments.token_to_instrument_map[instrument_token]
      