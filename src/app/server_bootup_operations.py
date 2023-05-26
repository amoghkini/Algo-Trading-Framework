from algo.algo_methods import AlgoMethods
from broker.broker_methods import BrokerMethods
from messaging_engine.producer import MessagingEngineProducer

def server_bootup_operations():
    AlgoMethods.save_algo_data()  # Add or save the data of algo table
    BrokerMethods.logout_all_brokers() # Change the broker status to logout 
    declare_exchange()  # declare the exchanges required for messaging queues.
    # TO DO: Login the admin broker. In this case we have only one broker.
    # TO DO: Start the algo 
    

def declare_exchange():
    message = MessagingEngineProducer()
    message.declare_exchange()