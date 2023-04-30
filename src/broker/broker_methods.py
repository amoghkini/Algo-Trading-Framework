from database.database_connection import get_db

class BrokerMethods:
    
    @staticmethod
    def add_new_broker(broker):
        conn = get_db()
        broker_data = broker.__dict__
        result = conn.insert("brokers", broker_data)
        if result:
            conn.commit()

    @staticmethod
    def test_connection():
        pass
    
    @staticmethod
    def get_all_brokers(user_name):
        conn = get_db()
        brokers = conn.getAll("brokers", ["broker_id", "broker_name", "status"], ("user_name = %s", [user_name]))
        if brokers == None:
            brokers = []
        
        return brokers
