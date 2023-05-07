from flask import render_template, redirect, url_for, flash, g
from flask.views import MethodView

from broker.broker import Broker
from broker.broker_methods import BrokerMethods
from exceptions.api_exceptions import DuplicateEntryError
from forms.broker_form import BrokerCreateForm

class AddBrokerAPI(MethodView):

    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        form = BrokerCreateForm()
        return render_template('add_broker.html', form=form)

    def post(self):
        try:
            if not g.user:
                return redirect(url_for('login_api'))

            form = BrokerCreateForm()
            broker_id: str = form.broker_id.data
            
            broker = Broker(broker_id)
            broker.broker_name = form.broker_name.data
            broker.password = form.password.data
            broker.app_key = form.app_key.data
            broker.app_secret_key = form.app_secret_key.data
            broker.totp_key = form.totp_key.data
            broker.auto_login = form.auto_login.data
            broker.user_name = g.user
            
            # Perform new broker addition
            BrokerMethods.add_new_broker(broker)
            
            flash("Broker added successfully. Please login and test the connection to activate the broker!!!", "success")
            return redirect(url_for('my_brokers_api'))
        
        except DuplicateEntryError as e:
            flash("The broker is already registered in the system. Please enquire brokers for more details", "danger")
            return render_template('add_broker.html', form=form)
        except Exception as e:
            flash("Something went wrong while adding the broker. Please retry after sometime.", "danger")
            return render_template('add_broker.html', form=form)
    