from flask.views import MethodView
import json
import logging
import threading
from config.Config import get_system_config
from core.Algo import Algo

class StartAlgoAPI(MethodView):
  def post(self):
    # start algo in a separate thread
    print("Amogh is here")
    x = threading.Thread(target=Algo.startAlgo)
    x.start()
    
    systemConfig = get_system_config()
    homeUrl = systemConfig['homeUrl'] + '?algoStarted=true'
    logging.info('Sending redirect url %s in response', homeUrl)
    respData = { 'redirect': homeUrl }
    return json.dumps(respData)
  