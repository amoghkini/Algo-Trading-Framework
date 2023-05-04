from database.postgres import PostgresSql
from flask import g
from os import environ

def get_db():
    if 'db' not in g:
        g.db = PostgresSql(
            host=environ.get('DB_HOST'),
            port=int(environ.get('DB_PORT')),
            db=environ.get('DB_SCHEMA'),
            user=environ.get('DB_USER'),
            password=environ.get('DB_PASSWORD'),
        )
    return g.db

