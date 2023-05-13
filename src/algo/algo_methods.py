from typing import Dict

from algo.algo import Algo
from algo.algo_status import AlgoStatus
from algo.messages import Messages
from config.config import ALGO_NAME
from database.database_connection import get_db
from database.database_schema import DatabaseSchema
from database.database_tables import DatabaseTables
from utils.utils import Utils

class AlgoMethods:
    
    @staticmethod
    def start_algorithm():
        # x = threading.Thread(target=Algo.start_algo)
        # x.start()
        Algo.start_algo()
        fields_to_update = {"status": AlgoStatus.RUNNING,
                            "start_time": Utils.get_epoch(),
                            "algo_start_reason": Messages.MANUALLY_STARTED_BY_USER
                            }
        AlgoMethods.update_algo_data(fields_to_update)
        
    @staticmethod
    def stop_algorithm():
        # x = threading.Thread(target=Algo.stop_algo)
        # x.start()
        Algo.stop_algo()
        fields_to_update = {"status": AlgoStatus.STOPPED,
                            "end_time": Utils.get_epoch(),
                            "algo_stop_reason": Messages.MANUALLY_STOPPED_BY_USER
                            }
        AlgoMethods.update_algo_data(fields_to_update)
    
    @staticmethod
    def update_algo_data(fields_to_update: Dict) -> int:
        conn = get_db()
        algo = conn.update(DatabaseSchema.ALGO_TRADER, DatabaseTables.ALGO, fields_to_update)
        if algo:
            conn.commit()
            return algo
        else:
            return None
    
    @staticmethod
    def save_algo_data() -> None:
        algo_data = {
            "name": ALGO_NAME,
            "status": AlgoStatus.STOPPED
        }
        conn = get_db()
        result: int = conn.insert_or_update(DatabaseSchema.ALGO_TRADER, DatabaseTables.ALGO, algo_data, 'name')
        if result:
            conn.commit()