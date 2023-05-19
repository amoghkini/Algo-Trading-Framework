from flask.views import MethodView

from broker.broker_methods import BrokerMethods


class HoldingsAPI(MethodView):

    def get(self):
        try:
            holdings: str = BrokerMethods.fetch_holdings()
            response_json = {"status": 'success',
                             "data": holdings}
        except Exception as e:
            response_json = {"status": "error",
                             "message": "Something went wrong while fetching holdings. Please try again after sometime."+str(e)}
        return response_json
