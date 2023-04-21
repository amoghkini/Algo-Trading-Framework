import logging
from flask import render_template, redirect, url_for, flash, request, g
from flask.views import MethodView

from brokers.broker import Broker
from core.controller import Controller
from common.broker_status import BrokerStatus
from database.database_connection import get_db
from forms.broker_form import BrokerLoginForm

class LogInBrokerAPI(MethodView):
        
    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        if 'brokerName' in request.args:
            broker_data = self.get_broker_data(request.args.get('brokerName'))
            
            login_method = request.args.get('loginMethod')
            form = BrokerLoginForm()  
            form.broker_name.data = broker_data.get('broker_name')
            form.broker_id.data = broker_data.get('broker_id')   
            form.totp_key.data = broker_data.get('totp_key')   
            form.login_method.data = login_method
            request.args = None
            #redirect_url = url_for('login_broker_api')
            #print(redirect_url,"Redirect url")
            return render_template('login_broker.html', form=form, login_method=login_method)
        else:
            return redirect(url_for('my_brokers_api'))
    
    def post(self):
        
        print(request.args)
        print(request.form)

        if not g.user:
            return redirect(url_for('login_api'))
        
        #r_stat ={"redirect": "/brokers"}
        #r_stat = {"status": "error",
        #          "message": "Something went wrong during broker login. Please try different method"}
        
        
        login_method = request.form.get('data[loginMethod]')
        
        if  login_method:
            broker_values = {"broker_id": request.form.get('data[brokerID]'),
                             "broker_name": request.form.get('data[brokerName]'),
                             "login_method": login_method 
            }
        else:    
            broker_values = {"broker_id": request.form.get('broker_id'),
                            "password": request.form.get('password'),
                             "broker_name": request.form.get('broker_name'),
                            "login_method": request.form.get('login_method'),
                            "encryption_token": request.form.get('enc_token'),
                            "app_key" : request.form.get('app_key'),
                            "app_secret": request.form.get('app_secret'),
                            "totp_key": request.form.get('totp_key')
            }
        print("broker_values post method", request.form)
        broker_data = self.get_broker_data(broker_values.get('broker_id'))
        
        #print("Broker values",broker_values)
        
        redirectUrl = Controller.handle_broker_login(request.args, broker_values)
        
        conn = get_db()
        if redirectUrl:
            r_stat = {"redirect": redirectUrl,
                    "broker_id": request.form.get('data[brokerID]'),
                    "login_method": login_method}
            return r_stat
        else:
            fields_to_update = {"access_token": "access_token",
                                "status": BrokerStatus.LOGGED_IN}

            status = conn.update("brokers", fields_to_update,
                                 ("broker_id=%s", (broker_values.get('broker_id'),)))
            print("status",status)
            if status:
                conn.commit()
            flash("Broker logged in successfully!!!","success")
            return redirect(url_for('my_brokers_api'))


    def get_broker_data(self, broker_id):
        conn = get_db()
        broker = conn.getOne(
            "brokers", ["id", "broker_id", "user_name", "broker_name", "password", "totp_key"], ("broker_id = %s", [broker_id]))
        if not broker:
            logging.error("The broker is not registered in the system or credentials are invalid.")
            flash("The broker is not registered in the system or credentials are invalid.", "danger")
            return redirect(url_for('my_brokers_api'))
        return broker
