from typing import Dict

from algo.algo import Algo
from algo.algo_status import AlgoStatus
from algo.messages import Messages
from config.config import ALGO_NAME
from database.database_connection import get_db
from database.database_schema import DatabaseSchema
from database.database_tables import DatabaseTables
from exceptions.api_exceptions import APIException
from utils.time_utils import TimeUtils


class AlgoMethods:
    
    @staticmethod
    def start_algorithm() -> None:
        # x = threading.Thread(target=Algo.start_algo)
        # x.start()
        Algo.start_algo()
        fields_to_update = {"status": AlgoStatus.RUNNING,
                            "start_time": TimeUtils.get_epoch(),
                            "algo_start_reason": Messages.MANUALLY_STARTED_BY_USER
                            }
        AlgoMethods.update_algo_data(fields_to_update)
        
    @staticmethod
    def stop_algorithm() -> None:
        # x = threading.Thread(target=Algo.stop_algo)
        # x.start()
        Algo.stop_algo()
        fields_to_update = {"status": AlgoStatus.STOPPED,
                            "end_time": TimeUtils.get_epoch(),
                            "algo_stop_reason": Messages.MANUALLY_STOPPED_BY_USER
                            }
        AlgoMethods.update_algo_data(fields_to_update)
    
    @staticmethod
    def algorithm_status() -> str:
        algo_data: Dict = AlgoMethods.get_algo_data()
        return algo_data.get('status')
    
    @staticmethod
    def save_algo_data() -> None:
        algo_data = {
            "name": ALGO_NAME,
            "status": AlgoStatus.STOPPED,
            "start_time": 0,
            "end_time": 0,
            "algo_start_reason": "",
            "algo_stop_reason": ""
        }
        conn = get_db()
        result: int = conn.insert_or_update(DatabaseSchema.ALGO_TRADER, DatabaseTables.ALGO, algo_data, 'name')
        if result:
            conn.commit()
            
    @staticmethod
    def get_algo_data() -> Dict:
        try:
            conn = get_db()
            algo_data: Dict = conn.get_one(DatabaseSchema.ALGO_TRADER, DatabaseTables.ALGO, '*')
            return algo_data
        except Exception as e:
            raise APIException("Something went wrong while fetching the algo details.")
    
    @staticmethod
    def update_algo_data(fields_to_update: Dict) -> int:
        conn = get_db()
        algo = conn.update(DatabaseSchema.ALGO_TRADER, DatabaseTables.ALGO, fields_to_update)
        if algo:
            conn.commit()
            return algo
        else:
            return None