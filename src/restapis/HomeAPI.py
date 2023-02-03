from flask.views import MethodView
from flask import render_template, request

class HomeAPI(MethodView):
    def get(self):
        return render_template('index.html')