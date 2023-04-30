from flask import render_template, g, redirect, url_for, flash
from flask.views import MethodView

from broker.broker_methods import BrokerMethods

class MyBrokersAPI(MethodView):

    def get(self):
        if not g.user:
            return redirect(url_for('dashboard_api'))
        try:
            brokers = BrokerMethods.get_all_brokers(g.user)
            return render_template('my_brokers.html',brokers = brokers)
        
        except Exception as e:
            flash("Something went wrong while fetching broker data. Please try after sometime", "danger")
            return redirect(url_for('dashboard_api'))
    
