from flask.views import MethodView

from broker.broker_methods import BrokerMethods


class PositionsAPI(MethodView):

    def get(self):
        try:
            positions: str = BrokerMethods.fetch_positiosn()
            response_json = {"status": 'success',
                             "data": positions}

        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while fetching positions. Please try again after sometime."+str(e)}
        return response_json
