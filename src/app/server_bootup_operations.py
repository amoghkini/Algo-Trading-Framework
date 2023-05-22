from algo.algo_methods import AlgoMethods
from messaging_engine.producer import MessagingEngineProducer

def server_bootup_operations():
    AlgoMethods.save_algo_data()  # Add or save the data of algo table
    declare_exchange()  # declare the exchanges required for messaging queues.
    # TO DO: Change the broker status to logout  
    

def declare_exchange():
    message = MessagingEngineProducer()
    message.declare_exchange()
