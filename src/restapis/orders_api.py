from flask.views import MethodView

from broker.broker_methods import BrokerMethods


class OrdersAPI(MethodView):

    def get(self):
        try:
            orders: str = BrokerMethods.fetch_orders()
            response_json = {"status": 'success',
                             "data": orders}

        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while fetching orders. Please try again after sometime."+str(e)}
        return response_json
