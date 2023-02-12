from flask import render_template, redirect, url_for, session
from flask.views import MethodView

class LogOutAPI(MethodView):

    def get(self):
        print("Inside get method")
        session.pop('user',None)
        return redirect(url_for('home_api'))

    
