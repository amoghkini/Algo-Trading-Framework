from flask.views import MethodView
from flask import url_for, flash
import json
import threading
from core.algo import Algo

class StartAlgoAPI(MethodView):
    def post(self):
        # start algo in a separate thread
        print("Amogh is here")
        x = threading.Thread(target=Algo.start_algo)
        x.start()
        
        '''
        systemConfig = get_system_config()
        homeUrl = systemConfig['homeUrl'] + '?algoStarted=true'
        logging.info('Sending redirect url %s in response', homeUrl)
        respData = { 'redirect': homeUrl }
        '''
        flash("Algo started successfully!!!","success")
        respData = {'redirect' : url_for('dashboard_api')}
        return json.dumps(respData)
    