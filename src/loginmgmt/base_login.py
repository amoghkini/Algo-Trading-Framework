class BaseLogin:

    def __init__(self, broker_app_details):
        self.broker_app_details = broker_app_details
        self.broker = broker_app_details.broker

    # Derived class should implement login function and return redirect url
    def login(self, args):
        pass

    def set_broker_handle(self, broker_handle):
        self.broker_handle = broker_handle

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_broker_app_details(self):
        return self.broker_app_details

    def get_access_token(self):
        return self.access_token

    def get_broker_handle(self):
        return self.broker_handle
