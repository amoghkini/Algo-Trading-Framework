from flask.views import MethodView
from flask import render_template


class DashboardAPI(MethodView):
    def get(self):
        return render_template('dashboard.html')
