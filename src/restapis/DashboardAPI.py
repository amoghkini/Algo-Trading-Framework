from flask.views import MethodView
from flask import render_template, flash, redirect, url_for
from forms.LoginUser import LoginForm


class DashboardAPI(MethodView):
    
    def get(self):
        form = LoginForm()
        return render_template('login.html',form = form)

    def post(self):
        return "inside post method"