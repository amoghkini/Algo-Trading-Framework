from database.mongo import MongoDB
from flask import g
from os import environ

def get_mongo_db() -> MongoDB:
    if 'mongo_db' not in g:
        g.mongo_db = MongoDB(
            host=environ.get('MONGO_HOST'),
            port=environ.get('MONGO_PORT'),
            db=environ.get('MONGO_DB')
        )
    return g.mongo_db