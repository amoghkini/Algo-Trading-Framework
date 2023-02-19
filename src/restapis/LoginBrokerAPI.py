import logging
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView


from common.BrokerStatus import BrokerStatus
from database.DatabaseConnection import conn
from loginmanagement.kiteext import KiteExt

class LoginBrokerAPI(MethodView):

    def get(self, method, broker_name, broker_id):
        broker = conn.getOne(
            "brokers", ["id", "broker_id", "user_name","password", "totp_key"], ("broker_id = %s", [broker_id]))
        if not broker:
            logging.error("The broker is not registered in the system or credentials are invalid.")
            flash("The broker is not registered in the system or credentials are invalid.", "danger")
            return redirect(url_for('my_brokers_api'))
        
        try:
            if (broker_name == 'Zerodha') and (method == 'creds') :
                
                global kite
                global access_token
                kite = KiteExt()
                kite.login_with_credentials(broker_id, broker.get('password'), broker.get('totp_key'))
                logging.info(kite.profile())
                access_token = kite.enctoken+"&user_id="+kite.user_id
                logging.info('access token = %s', access_token)
                logging.info('Login successful. access token = %s', access_token)
                print(access_token)
        
            #elif broker_name == 'Upstox':
            #    pass
            
            fields_to_update =  {"access_token":access_token,
                                    "status": BrokerStatus.LOGGED_IN}
            
            status = conn.update("brokers", fields_to_update,
                                ("broker_id=%s", (broker_id,)))
            if status:
                logging.info("Access token written successfully!!!")
                conn.commit()
            else:
                logging.exception("Exception occured while writing the access token %s", e)
                flash("Something went wrong while writing access token", "danger")
                return redirect(url_for('my_brokers_api'))
                

                
            flash("Logged in to the broker successfully", "success")
        except Exception as e:
            logging.exception("Exception occured while logging to the broker %s",e)
            flash("Something went wrong during broker login","danger")
        return redirect(url_for('my_brokers_api'))
        #return 'amogh is here with login method ' + broker_name + broker_id
