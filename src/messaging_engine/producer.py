import json
import logging
import pika

from common.singleton import SingletonMeta


class MessagingEngineProducer(metaclass=SingletonMeta):

    __instance = None
    
    def __init__(self, queue="message_priority1") -> None:
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=0))
        self.__channel = self.__connection.channel()
        self.queue = queue
    
    def declare_exchange(self) -> None:
        self.__channel.exchange_declare(
            exchange='messaging_engine', 
            exchange_type='direct')
    
    def publish(self, payload={}):
        self.__channel.basic_publish(
            exchange='messaging_engine',
            routing_key='message_priority1',
            body=json.dumps(payload)
        )
        logging.info("The message has been published successfully.")
        #self.__connection.close()
        
    def close_connection(self):
        self.__connection.close()