import os
import re
import secrets

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.hash import sha256_crypt
from PIL import Image


from database.DatabaseConnection import conn


class Broker:
    
    @staticmethod
    def fetch_one_broker(broker_id):

        user = conn.getOne("users", '*', ("broker_id = %s", [broker_id]))
        if user:
            return user
        else:
            return None


