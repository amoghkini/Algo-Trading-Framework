from database.MySQL import SimpleMysql

class User:
    db = None
    def __init__(self) -> None:
        
        try:
            self.db = SimpleMysql(
                host="127.0.0.1",
                db="algo_trader_framework",
                user="root",
                passwd="root",
                keep_alive=True  # try and reconnect timedout mysql connections?
            )
            print("Db connected successfully")
        except Exception as e:
            print("Error while connecting the database")

    def add_new_user(self,form):
        self.db.insert("users",{"name": form.username.data, "email": form.email.data, "password": form.password.data})
        self.db.commit()
        return True

    def fetch_one_user(self,form):
        user = self.db.getOne("users",["email","password"],("name = %s and password = %s",[form.email.data,form.password.data]))
        if user:
            print("User found")
            return True
        else:
            return False
