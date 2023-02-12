from flask import render_template, redirect, url_for
from flask.views import MethodView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required


class LogOutAPI(MethodView):

    def get(self):
        print("Inside get method")
        logout_user()
        return redirect(url_for('home_api'))

    
