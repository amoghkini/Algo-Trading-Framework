import pika
import json
import uuid

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=0))
# channel = connection.channel()
        
# channel.exchange_declare(
#     exchange='messaging_engine',
#     exchange_type='direct'
# )

# order = {
#     'id': str(uuid.uuid4()),
#     'user_email': 'amogh@example.com',
#     'product': 'new product'
# }


# channel.basic_publish(
#     exchange='messaging_engine',
#     routing_key='message_priority1',
#     body=json.dumps({'user_email': order.get('user_email')})
# )

# print(' [x] sent notify message')

# channel.basic_publish(
#     exchange='messaging_engine',
#     routing_key='message_priority1',
#     body=json.dumps(order)
# )

# print(' [x] sent notify entire message')

# connection.close()

class MessagingEngineProducer:
    
    # This should be a singletone class. Refer https://www.youtube.com/watch?v=Wiw7oOgBjFs&t=107s at 12:30 for the same.
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
        print("The message has been published successfully.")
        self.__connection.close()