from flask import flash, redirect, url_for, request
from flask.views import MethodView

from broker.broker_methods import BrokerMethods
from broker.broker_status import BrokerStatus
from database.database_connection import get_db
from database.database_schema import DatabaseSchema
from exceptions.broker_exceptions import BrokerNotFoundError

class LogOutBrokerAPI(MethodView):

    def get(self):
        try:
            broker_id: str = request.args.get('brokerID')
            if broker_id == None:
                raise BrokerNotFoundError("Please provide the valid broker")
            
            status = BrokerMethods.logout_broker(broker_id)
            if not status:
                BrokerNotFoundError("Requested broker not found!!!")
                
            flash("Broker logged out successfully!!!", "success")
            return redirect(url_for('my_brokers_api'))
        except BrokerNotFoundError as e:
            flash(str(e), "danger")
            return redirect(url_for('my_brokers_api'))
        except Exception as e:
            flash("Something went wrong during broker log out", "danger")
            return redirect(url_for('my_brokers_api'))