from database.DatabaseConnection import conn
from database.MySQL import Mysql

class User:
    '''
    db = None
    def __init__(self) -> None:
        
        try:
            self.db = Mysql(
                host="127.0.0.1",
                db="algo_trader_framework",
                user="root",
                passwd="root",
                keep_alive=True  # try and reconnect timedout mysql connections?
            )
            print("Db connected successfully")
        except Exception as e:
            print("Error while connecting the database")
    '''
    @staticmethod
    def add_new_user(form):
        conn.insert("users",{"name": form.username.data, "email": form.email.data, "password": form.password.data})
        conn.commit()
        return True

    @staticmethod
    def fetch_one_user(form):
        user = conn.getOne("users", ["email", "password"], ("name = %s and password = %s", [
                           form.email.data, form.password.data]))
        #user = Mysql.getOne("users", ["email", "password"], ("name = %s and password = %s", [form.email.data, form.password.data]))
        if user:
            print("User found",user)
            return True
        else:
            return False
