import pandas as pd
from flask import render_template, g, redirect, url_for, flash
from flask.views import MethodView
from typing import List

from broker.broker_methods import BrokerMethods
from exceptions.strategy_exceptions import StrategyNotFoundError
from strategies.strategy_methods import StrategyMethods

class MyStrategiesAPI(MethodView):

    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        try:
            strategies: pd.DataFrame = StrategyMethods.get_all_strategies(g.user)
            return render_template('strategies.html', strategies=strategies.to_dict())
        
        except StrategyNotFoundError as e:
            flash(str(e),'danger')
            return redirect(url_for('dashboard_api'))
        except Exception as e:
            print(e)
            flash("Something went wrong while fetching strategies data. Please try after sometime", "danger")
            return redirect(url_for('dashboard_api'))