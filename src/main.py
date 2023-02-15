import os
import logging
from datetime import timedelta
from flask import Flask, g, render_template, session


from config.Config import get_server_config
from restapis.AboutUsAPI import AboutUsAPI
from restapis.ChangePasswordAPI import ChangePasswordAPI
from restapis.DashboardAPI import DashboardAPI
from restapis.HomeAPI import HomeAPI
from restapis.LogInAPI import LogInAPI
from restapis.LogOutAPI import LogOutAPI
from restapis.MyProfileAPI import MyProfileAPI
from restapis.RequestPassResetAPI import RequestPassResetAPI
from restapis.ResetPasswordAPI import ResetPasswordAPI
from restapis.SignUpAPI import SignUpAPI

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'AMOGH kini'


app.add_url_rule("/", view_func=HomeAPI.as_view("home_api"))
app.add_url_rule("/about", view_func=AboutUsAPI.as_view("about_us_api"))
app.add_url_rule("/change_password", view_func=ChangePasswordAPI.as_view("change_password_api"))
app.add_url_rule("/dashboard", view_func=DashboardAPI.as_view("dashboard_api"))
app.add_url_rule("/login", view_func=LogInAPI.as_view("login_api"))
app.add_url_rule("/logout", view_func=LogOutAPI.as_view("logout_api"))
app.add_url_rule("/profile", view_func=MyProfileAPI.as_view("my_profile_api"))
app.add_url_rule("/reset_password/<token>", view_func=ResetPasswordAPI.as_view("reset_password_api"))
app.add_url_rule("/reset_password_request", view_func=RequestPassResetAPI.as_view("reset_password_request_api"))
app.add_url_rule("/signup", view_func=SignUpAPI.as_view("sign_up_api"))


def initLoggingConfg(filepath):
  format = "%(asctime)s: %(message)s"
  logging.basicConfig(filename=filepath, format=format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


server_config = get_server_config()

deployDir = server_config.get('deployDir')
if os.path.exists(deployDir) == False:
  print("Deploy Directory " + deployDir + " does not exist. Exiting the app.")
  exit(-1)

logFileDir = server_config.get('logFileDir')
if os.path.exists(logFileDir) == False:
  print("LogFile Directory " + logFileDir +
        " does not exist. Exiting the app.")
  exit(-1)

print("Deploy  Directory = " + deployDir)
print("LogFile Directory = " + logFileDir)
initLoggingConfg(logFileDir + "/app.log")

logging.info('server_config => %s', server_config)


port = server_config.get('port')


@app.before_request
def before_request():
  session.permanent = True  # set session to use PERMANENT_SESSION_LIFETIME
  session.modified = True   # reset the session timer on every request
  app.permanent_session_lifetime = timedelta(minutes=10)

  g.user = None
  if 'user' in session:
    g.user = session['user']

  g.secret_key = "AMOGH kini"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(port=port)
