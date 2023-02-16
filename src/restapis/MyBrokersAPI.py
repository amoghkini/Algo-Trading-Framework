from flask import render_template
from flask.views import MethodView


class MyBrokersAPI(MethodView):

    def get(self):
        return render_template('my_brokers.html')
    
    def post(self):
        return
