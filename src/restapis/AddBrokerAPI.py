from flask import render_template
from flask.views import MethodView


class AddBrokerAPI(MethodView):

    def get(self):
        return render_template('broker.html')
