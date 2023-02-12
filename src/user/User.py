from database.DatabaseConnection import conn
from database.MySQL import Mysql

class User:
    
    @staticmethod
    def add_new_user(form):
        conn.insert("users",{"name": form.username.data, "email": form.email.data, "password": form.password.data})
        conn.commit()
        return True

    @staticmethod
    def fetch_one_user(form):
        user = conn.getOne("users", ["id","email", "password"], ("name = %s and password = %s", [
                           form.email.data, form.password.data]))
        if user:
            print("User found",user)
            return user
        else:
            return None
