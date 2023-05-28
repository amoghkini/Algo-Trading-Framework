import pandas as pd
from typing import List

from database.database_connection import get_db
from database.database_schema import DatabaseSchema
from database.database_tables import DatabaseTables
from exceptions.strategy_exceptions import StrategyNotFoundError


class StrategyMethods:

    @staticmethod
    def get_all_strategies(user_name: str) -> List:
        try:
            conn = get_db()
            strategies: List = conn.get_all(DatabaseSchema.ALGO_TRADER, DatabaseTables.STRATEGIES, [
                                            "name", "start_timestamp", "stop_timestamp", "square_off_timestamp", "capital", "is_fno", "capital_per_set"], ("user_name = %s", [user_name]))
            if strategies == None:
                strategies = []
            else:
                strategies = pd.DataFrame(strategies)
            return strategies
        except Exception as e:
            raise StrategyNotFoundError("Something went wrong while fetching the strategies."+str(e))