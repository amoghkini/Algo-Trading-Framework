from broker.broker_login_status import BrokerLoginStatus
from broker.broker_status import BrokerStatus
from utils.utils import Utils

class Broker:
    
    def __init__(self, broker_id: str) -> None:
        self.broker_id: str = broker_id
        self.broker_name: str = ''
        self.password: str = ''
        self.user_name: str = ''
        self.app_key: str = ''
        self.app_secret_key: str = ''
        self.totp_key: str = ''
        self.auto_login: bool = ''
        self.status: str = BrokerStatus.CREATED
        self.broker_addition_date: int = Utils.get_epoch()
        self.login_status: str = BrokerLoginStatus.YET_TO_LOGIN