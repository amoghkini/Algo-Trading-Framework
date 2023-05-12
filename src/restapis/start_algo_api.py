import threading
from flask.views import MethodView

from algo.algo import Algo
from exceptions.broker_exceptions import BrokerNotFoundError

class StartAlgoAPI(MethodView):
    
    def get(self):
        try:
            #x = threading.Thread(target=Algo.start_algo)
            #x.start()
            Algo.start_algo()
            response_json = {"status": 'success',
                            "message": "Algo started successfully"}
        except BrokerNotFoundError as e:
            response_json = {"status": "fail",
                             "message": str(e)}
        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while starting the algo. Please try again after sometime."}
        return response_json
    