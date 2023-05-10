from typing import Dict, List

from broker.broker import Broker
from broker.broker_login_status import BrokerLoginStatus
from core.controller import Controller
from database.database_connection import get_db
from database.database_schema import DatabaseSchema
from database.database_tables import DatabaseTables
from exceptions.api_exceptions import DatabaseWriteError
from exceptions.broker_exceptions import BrokerNotFoundError
from utils.utils import Utils

class BrokerMethods:
    
    @staticmethod
    def add_new_broker(broker: Broker) -> None:
        conn = get_db()
        broker_data: Dict = broker.__dict__
        result: int = conn.insert(DatabaseSchema.ALGO_TRADER, DatabaseTables.BROKERS, broker_data)
        if result:
            conn.commit()  
    
    @staticmethod
    def get_broker_data(broker_id: str) -> Dict:
        try:
            conn = get_db()
            broker: Dict = conn.get_one(DatabaseSchema.ALGO_TRADER, DatabaseTables.BROKERS, '*', ("broker_id = %s", [broker_id]))
            return broker
        except Exception as e:
            raise BrokerNotFoundError("Something went wrong while fetching the broker details.")
    
    @staticmethod
    def get_all_brokers(user_name: str) -> List:
        try:
            conn = get_db()
            brokers: List = conn.get_all(DatabaseSchema.ALGO_TRADER, DatabaseTables.BROKERS, ["broker_id", "broker_name", "status", "login_status","auto_login"], ("user_name = %s", [user_name]))
            if brokers == None:
                brokers = []
            return brokers
        except Exception as e:
            raise BrokerNotFoundError("Something went wrong while fetching the brokers.")

    @staticmethod
    def login_broker(args, broker: Dict):
        broker_id: str = broker.get('broker_id')
        
        # Read the broker data
        broker_data: Dict = BrokerMethods.get_broker_data(broker_id)
        
        # Add app_key, app_seecret_key, totp_key in the dictionary
        broker['app_key'] = broker_data.get('app_key')
        broker['app_secret_key'] = broker_data.get('app_secret_key')
        broker['totp_key'] = broker_data.get('totp_key')
        redirect_url = Controller.handle_broker_login(args, broker)
        if redirect_url:
            r_stat = {"redirect": redirect_url}
            return r_stat
        else:
            fields_to_update = {"login_status": BrokerLoginStatus.LOGGED_IN}
            # Insert or update method to insert the auth token in new table
            status = BrokerMethods.update_broker(fields_to_update, broker_id)
            if status:
                if 'login_required' in args:
                    return status
                else:
                    redirect_external_url: str = Utils.get_external_url('my_brokers_api')
                    r_stat = {"redirect": redirect_external_url,
                              "alert_message": "The broker is already logged in using this method. No further action is required."}
                    return r_stat
            else:
                return None

    @staticmethod
    def logout_broker(broker_id: str) -> int:
        fields_to_update = {"login_status": BrokerLoginStatus.LOGGED_OUT}
        status = BrokerMethods.update_broker(fields_to_update, broker_id)
        if status:
            return status
        else:
            return None
    
    @staticmethod
    def test_connection():
        # Check with saved auth token if we are able to fetch the boker details. If not then throw error.
        pass
    
    @staticmethod
    def update_broker(fields_to_update: Dict, broker_id: str):
        try:
            conn = get_db()
            broker_update_count: int = conn.update(
                DatabaseSchema.ALGO_TRADER, DatabaseTables.BROKERS, fields_to_update, ("broker_id=%s", (broker_id,)))
            if broker_update_count:
                conn.commit()
                return broker_update_count
            else:
                return None
        except Exception as e:
            raise DatabaseWriteError("Something went wrong while updating the broker data")
        
    @staticmethod
    def save_access_token(access_token_data: Dict) -> None:
        conn = get_db()
        result: int = conn.insert_or_update(
            DatabaseSchema.ALGO_TRADER, DatabaseTables.ACCESS_TOKENS, access_token_data, 'broker_id,token_date')
        if result:
            conn.commit()
        return
    
    @staticmethod
    def get_access_token(broker_id: str) -> str:
        conn = get_db()
        todays_date: str = Utils.get_today_date_str()
        result: Dict = conn.get_one(DatabaseSchema.ALGO_TRADER, DatabaseTables.ACCESS_TOKENS,
                                         ["access_token"], ("broker_id = %s and token_date = %s", [broker_id, todays_date]))
        if result:
            return result.get('access_token')
        else:
            return None
