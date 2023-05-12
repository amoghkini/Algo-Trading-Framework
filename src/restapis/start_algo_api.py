import json
import threading
from flask.views import MethodView
from flask import url_for, flash

from algo.algo import Algo

class StartAlgoAPI(MethodView):
    
    def get(self):
        try:
            x = threading.Thread(target=Algo.start_algo)
            x.start()
            response_json = {"status": 'success',
                            "message": "Algo started successfully"}
        except Exception as e:
            response_json = {"status": "fail",
                             "message": "Something went wrong while starting the algo. Please try after sometime."}
        return response_json
    