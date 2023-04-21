from database.my_sql import Mysql
from flask import g

def get_db():
    if 'db' not in g:
        g.db = Mysql(
            host="127.0.0.1",
            db="algo_trader_framework",
            user="root",
            passwd="root",
            keep_alive=True  # try and reconnect timedout mysql connections?
        )
    return g.db

