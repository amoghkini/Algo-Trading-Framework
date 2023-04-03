from flask import flash, redirect, render_template, url_for, session, request
from flask.views import MethodView

from common.broker_status import BrokerStatus
from database.database_connection import conn


class LogOutBrokerAPI(MethodView):

    def get(self):
        print("Inside get method")
        # Need to implement actual broker logout logic similar to login logic.
        
        print(request.args)
        fields_to_update = {"access_token": "",
                            "status": BrokerStatus.LOGGED_OUT}

        status = conn.update("brokers", fields_to_update,
                              ("broker_id=%s", (request.args.get('brokerID'),)))
        print("status", status)
        
        if status:
            conn.commit()
            flash("Broker logged out successfully!!!", "success")
        return redirect(url_for('my_brokers_api'))
