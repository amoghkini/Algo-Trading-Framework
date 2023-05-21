import sys
from dotenv import load_dotenv
from messaging_engine.consumer import MessaginEngineConsumer

load_dotenv('../.env')


def main():
    consumer = MessaginEngineConsumer()
    consumer.start_consumer()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("Keyboard interrupt error occured")
    except Exception as e:
        print("Exception occured!!!",e)
        sys.exit(0)