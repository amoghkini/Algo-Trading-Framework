from flask.views import MethodView

from algo.algo_methods import AlgoMethods
from exceptions.broker_exceptions import BrokerNotFoundError

class StopAlgoAPI(MethodView):

    def get(self):
        try:
            AlgoMethods.stop_algorithm()
            response_json = {"status": 'success',
                             "message": "Algo stopped successfully"}
        except BrokerNotFoundError as e:
            response_json = {"status": "fail",
                             "message": str(e)}
        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while stopping the algo. Please try again after sometime."+str(e)}
        return response_json
