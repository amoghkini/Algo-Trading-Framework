from flask import render_template, g, redirect, url_for
from flask.views import MethodView

class HomeAPI(MethodView):
    def get(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        return render_template('index.html')