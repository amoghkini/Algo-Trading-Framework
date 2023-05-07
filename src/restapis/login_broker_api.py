import logging
from flask import render_template, redirect, url_for, flash, request, g
from flask.views import MethodView
from typing import Dict

from broker.broker_methods import BrokerMethods
from exceptions.broker_exceptions import BrokerError
from forms.broker_form import BrokerLoginForm

class LogInBrokerAPI(MethodView):
        
    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        try:
            if 'loginMethod' in request.args:
                form = BrokerLoginForm()  
                form.broker_name.data = request.args.get('brokerName')
                form.broker_id.data = request.args.get('brokerId')
                form.login_method.data = request.args.get('loginMethod')
                request.args = None
                return render_template('login_broker.html', form=form)
            else:
                flash("Invalid login method!!!","danger")
                return redirect(url_for('my_brokers_api'))
        except Exception as e:
            flash("Something went wrong. Please try after sometime!!!", "danger")
            return redirect(url_for('my_brokers_api'))
    
    def post(self):
        if not g.user:
            return redirect(url_for('login_api'))
        try:   
            if 'login_method' in request.args:
                # To redirct the user to login page. This will handle the broker login from our portal.
                broker: Dict = {"broker_id": request.form.get('data[brokerID]'),
                                "broker_name": request.form.get('data[brokerName]'),
                                "login_method": request.args.get('login_method')
                                }
            elif 'login_required' in request.args:
                # For broker login using our portal
                broker: Dict = {"broker_id": request.form.get('broker_id'),
                                "password": request.form.get('password'),
                                "broker_name": request.form.get('broker_name'),
                                "login_method": request.form.get('login_method'),
                                "encryption_token": request.form.get('enc_token')
                                }
            else:
                # For broker login using brokers API
                # Need to figure out how can we get the broker id from broker respose.
                broker: Dict = dict()
                
            redirect_handler = BrokerMethods.login_broker(request.args, broker)
            if isinstance(redirect_handler, dict):
                return redirect_handler
            elif isinstance(redirect_handler, int):
                flash("Broker logged in successfully. Please test the connection!!!",'success')
                return redirect(url_for('my_brokers_api'))
            else:
                raise BrokerError("Something went wrong while storing the broker key!!!")
        except Exception as e:
            flash("Something went wrong during broker log in!!!",'danger')
            return redirect(url_for('my_brokers_api'))