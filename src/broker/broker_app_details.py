class BrokerAppDetails:
    def __init__(self, broker):
        self.broker = broker
        self.app_key = None
        self.app_secret = None

    def set_client_id(self, client_id):
        self.client_id = client_id

    def set_app_key(self, app_key):
        self.app_key = app_key

    def set_app_secret(self, app_secret):
        self.app_secret = app_secret

