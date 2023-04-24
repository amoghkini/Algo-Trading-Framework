from database.my_sql import Mysql
from flask import g
from os import environ

def get_db():
    if 'db' not in g:
        g.db = Mysql(
            host=environ.get('DB_HOST'),
            port=int(environ.get('DB_PORT')),
            db=environ.get('DB_SCHEMA'),
            user=environ.get('DB_USER'),
            passwd=environ.get('DB_PASSWORD'),
            keep_alive=True  # try and reconnect timedout mysql connections?
        )
    return g.db

