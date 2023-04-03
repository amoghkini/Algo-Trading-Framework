from flask import render_template
from flask.views import MethodView


class EnquireBrokerAPI(MethodView):

    def get(self,broker_id):
        header = "Brokers Enquiry"
        return render_template('broker.html', header = header )
