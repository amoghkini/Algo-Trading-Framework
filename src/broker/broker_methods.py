from database.database_connection import get_db
from database.database_schema import DatabaseSchema

class BrokerMethods:
    
    @staticmethod
    def add_new_broker(broker):
        conn = get_db()
        broker_data = broker.__dict__
        result = conn.insert(DatabaseSchema.ALGO_TRADER,
                             "brokers", broker_data)
        if result:
            conn.commit()

    @staticmethod
    def test_connection():
        # Check with saved auth token if we are able to fetch the boker details. If not then throw error.
        pass
    
    @staticmethod
    def get_all_brokers(user_name):
        conn = get_db()
        brokers = conn.get_all(DatabaseSchema.ALGO_TRADER, "brokers", ["broker_id", "broker_name", "status"], ("user_name = %s", [user_name]))
        if brokers == None:
            brokers = []
        
        return brokers
