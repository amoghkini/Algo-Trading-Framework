from flask import render_template, redirect, url_for
from flask.views import MethodView


class LogOutAPI(MethodView):

    def get(self):
        print("Inside get method")
        return redirect(url_for('home_api'))

    
