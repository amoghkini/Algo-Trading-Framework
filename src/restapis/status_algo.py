from flask.views import MethodView

from algo.algo_methods import AlgoMethods
from exceptions.api_exceptions import APIException


class StatusAlgoAPI(MethodView):

    def get(self):
        try:
            algo_status: str = AlgoMethods.algorithm_status()
            response_json = {"status": 'success',
                             "algoStatus": algo_status}
        except APIException as e:
            response_json = {"status": "fail",
                             "message": str(e)}
        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while stopping the algo. Please try again after sometime."+str(e)}
        return response_json
