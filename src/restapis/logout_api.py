from flask import flash, redirect, url_for, session
from flask.views import MethodView

class LogOutAPI(MethodView):

    def get(self):
        session.pop('user',None)
        flash("User logged out successfully",'success')
        return redirect(url_for('my_brokers_api'))
