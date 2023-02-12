from flask import render_template, request
from flask.views import MethodView

class HomeAPI(MethodView):
    def get(self):
        return render_template('index.html')