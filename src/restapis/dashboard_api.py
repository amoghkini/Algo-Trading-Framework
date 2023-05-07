from flask import render_template, redirect, url_for, g
from flask.views import MethodView

class DashboardAPI(MethodView):
    
    def get(self):
        if g.user:
            return render_template('dashboard.html')
        return redirect(url_for('login_api'))
