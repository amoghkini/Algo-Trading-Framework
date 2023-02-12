from flask.views import MethodView
from flask import render_template, flash, redirect, url_for, session, g
from forms.LoginUser import LoginForm


class DashboardAPI(MethodView):
    
    def get(self):
        if g.user:
            return render_template('dashboard.html')
        return redirect(url_for('login_api'))

    def post(self):
        return "inside post method"