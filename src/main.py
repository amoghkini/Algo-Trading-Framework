import os
import logging
from datetime import timedelta
from flask import Flask, g, render_template, session

from config.config import get_server_config
from restapis.about_us_api import AboutUsAPI
from restapis.add_broker_api import AddBrokerAPI
from restapis.change_password_api import ChangePasswordAPI
from restapis.dashboard_api import DashboardAPI
from restapis.enquire_broker_api import EnquireBrokerAPI
from restapis.home_api import HomeAPI
from restapis.login_api import LogInAPI
from restapis.login_broker_api import LogInBrokerAPI
from restapis.logout_broker_api import LogOutBrokerAPI
from restapis.logout_api import LogOutAPI
from restapis.my_brokers_api import MyBrokersAPI
from restapis.my_profile_api import MyProfileAPI
from restapis.request_pass_reset_api import RequestPassResetAPI
from restapis.reset_password_api import ResetPasswordAPI
from restapis.sign_up_api import SignUpAPI
from restapis.start_algo_api import StartAlgoAPI
from utils.logger import config_root_logger
from utils.utils import Utils


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'AMOGH kini'


app.add_url_rule("/", view_func=HomeAPI.as_view("home_api"))
app.add_url_rule("/about", view_func=AboutUsAPI.as_view("about_us_api"))
app.add_url_rule("/algo/start", view_func=StartAlgoAPI.as_view("start_algo_api"))
app.add_url_rule("/broker/add", view_func=AddBrokerAPI.as_view("add_broker_api"))
app.add_url_rule("/broker/enquire/<broker_id>", view_func=EnquireBrokerAPI.as_view("broker_enquiry_api"))
app.add_url_rule("/broker/login", view_func=LogInBrokerAPI.as_view("login_broker_api"))
app.add_url_rule("/broker/logout", view_func=LogOutBrokerAPI.as_view("logout_broker_api"))
app.add_url_rule("/brokers", view_func=MyBrokersAPI.as_view("my_brokers_api"))
app.add_url_rule("/change_password", view_func=ChangePasswordAPI.as_view("change_password_api"))
app.add_url_rule("/dashboard", view_func=DashboardAPI.as_view("dashboard_api"))
app.add_url_rule("/login", view_func=LogInAPI.as_view("login_api"))
app.add_url_rule("/logout", view_func=LogOutAPI.as_view("logout_api"))
app.add_url_rule("/profile", view_func=MyProfileAPI.as_view("my_profile_api"))
app.add_url_rule("/reset_password/<token>", view_func=ResetPasswordAPI.as_view("reset_password_api"))
app.add_url_rule("/reset_password_request", view_func=RequestPassResetAPI.as_view("reset_password_request_api"))
app.add_url_rule("/signup", view_func=SignUpAPI.as_view("sign_up_api"))


server_config = get_server_config()

deploy_dir = server_config.get('deployDir')
if os.path.exists(deploy_dir) == False:
    print("Deploy Directory " + deploy_dir +
          " does not exist. Exiting the app.")
    exit(-1)

log_file_dir = server_config.get('logFileDir')
if os.path.exists(log_file_dir) == False:
    print("LogFile Directory " + log_file_dir +
          " does not exist. Exiting the app.")
    exit(-1)

print("Deploy  Directory = " + deploy_dir)
print("LogFile Directory = " + log_file_dir)

config_root_logger(log_file_dir + "/app.log")

logging.info('server_config => %s', server_config)

port = server_config.get('port')

@app.before_request
def before_request():
    session.permanent = True  # set session to use PERMANENT_SESSION_LIFETIME
    session.modified = True   # reset the session timer on every request
    app.permanent_session_lifetime = timedelta(minutes=60)

    g.user = None
    if 'user' in session:
        g.user = session['user']

    g.secret_key = "Amogh kini"
    
    # Async method can be written which will be called in before requst method
    # which will fetch the nifty and bank nifty price on each page reload
    # before implementing the websocket apporach.

    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":  
    app.run(host = "0.0.0.0", port=port)
