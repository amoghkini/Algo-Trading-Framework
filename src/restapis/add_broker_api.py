import logging
from flask import render_template, redirect, url_for, flash, g
from flask.views import MethodView

from broker.broker_status import BrokerStatus
from database.database_connection import get_db
from forms.broker_form import BrokerCreateForm

class AddBrokerAPI(MethodView):

    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        form = BrokerCreateForm()
        return render_template('add_broker.html', form=form)


    def post(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        form = BrokerCreateForm()
        
        # check if broker is alrady present in the system
        conn = get_db()
        broker = conn.getOne(
            "brokers", ["id", "broker_id", "user_name"], ("broker_id = %s", [form.user_id.data]))
        if broker:
            logging.error("The broker with same username already exist in the system.")
            flash("The broker with same username already exist in the system.","danger")
            return render_template('add_broker.html', form=form)
        
        
        # add the new broker into syatem
        
        broker_data = self.add_broker_dict(form)
        try:
            result = conn.insert("brokers",broker_data)
            if result != None:
                conn.commit()
            else:
                logging.exception("Exception occured while adding new broker.")
                flash(
                    "Something went wrong while adding the broker. Please retry after sometime.","danger")
                return render_template('add_broker.html', form=form)
            
        except Exception as e:
            logging.exception("Exception occured while adding new broker.")
            flash(
                "Something went wrong while adding the broker. Please retry after sometime.", "danger")
            return render_template('add_broker.html', form=form)
        
        flash("Broker added successfully. Please test the connection to activate the broker!!!","success")
        return redirect(url_for('my_brokers_api'))
    
    def add_broker_dict(self,form):
        broker_data = {"broker_id" : form.user_id.data,
                       "broker_name" : form.broker_name.data,
                       "password" : form.password.data,
                       "user_name" : g.user,
                       "totp_key" : form.totp_key.data,
                       "auto_login" : 0,
                       "status" : BrokerStatus.CREATED,
                       "broker_addition_date" : 1231231
                       }
        return broker_data
        