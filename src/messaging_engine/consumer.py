import pika
import json
from messaging_engine.email import Email

# Connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = Connection.channel()

# queue = channel.queue_declare('message_priority1')
# queue_name = queue.method.queue

# channel.queue_bind(
#     exchange='messaging_engine',
#     queue=queue_name,
#     routing_key='message_priority1'
# )


# def callback(ch, method, properties, body):
#     payload = json.loads(body)
#     print("Notifying", payload)
#     Email.send_mail(payload)
#     ch.basic_ack(delivery_tag=method.delivery_tag)


# channel.basic_consume(on_message_callback=callback, queue='message_priority1')

# print("waiting for messages")

# channel.start_consuming()

class MessaginEngineConsumer:
    def __init__(self) -> None:
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.__channel = self.__connection.channel()
    
    def start_consumer(self):
        queue = self.__channel.queue_declare('message_priority1')


        queue_name = queue.method.queue
        self.__channel.queue_bind(
            exchange='messaging_engine',
            queue=queue_name,
            routing_key='message_priority1'
        )

        def callback(ch, method, properties, body):
            payload = json.loads(body)
            Email.send_mail(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            

        self.__channel.basic_consume(on_message_callback=callback, queue='message_priority1')

        print("waiting for messages")

        self.__channel.start_consuming()