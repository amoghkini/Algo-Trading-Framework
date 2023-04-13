import logging

from core.controller import Controller

class BaseTicker:
    def __init__(self, broker):
        self.broker = broker
        self.broker_login = Controller.get_broker_login()
        self.ticker = None
        self.tick_listeners = []

    def start_ticker(self):
        pass

    def stop_ticker(self):
        pass

    def register_listener(self, listener):
        # All registered tick listeners will be notified on new ticks
        self.tick_listeners.append(listener)

    def register_symbols(self, symbols):
        pass

    def unregister_symbols(self, symbols):
        pass

    def on_new_ticks(self, ticks):
        # logging.info('New ticks received %s', ticks)
        for tick in ticks:
            for listener in self.tick_listeners:
                try:
                    listener(tick)
                except Exception as e:
                    logging.error('BaseTicker: Exception from listener callback function. Error => %s', str(e))

    def onConnect(self):
        logging.info('Ticker connection successful.')

    def onDisconnect(self, code, reason):
        logging.error('Ticker got disconnected. code = %d, reason = %s', code, reason)

    def onError(self, code, reason):
        logging.error('Ticker errored out. code = %d, reason = %s', code, reason)

    def onReconnect(self, attemptsCount):
        logging.warn('Ticker reconnecting.. attemptsCount = %d', attemptsCount)

    def onMaxReconnectsAttempt(self):
        logging.error('Ticker max auto reconnects attempted and giving up..')

    def onOrderUpdate(self, data):
        #logging.info('Ticker: order update %s', data)
        pass
