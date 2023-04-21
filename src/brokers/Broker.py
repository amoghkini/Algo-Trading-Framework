from database.database_connection import get_db

class Broker:
    
    @staticmethod
    def fetch_one_broker(broker_id):
        """
        Fetches a single broker from the "users" table in the database using their unique identifier.

        Args:
            broker_id (int): The unique identifier of the broker.

        Returns:
            dict or None: A dictionary containing the details of the broker if they are found in the database, otherwise returns `None`.

        Raises:
            None.

        Example:
            >>> fetch_one_broker(123)
            {'id': 123, 'name': 'John Doe', 'email': 'johndoe@example.com', 'broker_id': 123}
        """
        conn = get_db()
        user = conn.getOne("users", '*', ("broker_id = %s", [broker_id]))
        if user:
            return user
        else:
            return None


