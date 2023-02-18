from flask import render_template, g, redirect, url_for, flash
from flask.views import MethodView

from database.DatabaseConnection import conn

class MyBrokersAPI(MethodView):

    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        brokers = conn.getAll(
            "brokers", ["broker_id", "broker_name","status"], ("user_name = %s", [g.user]))
        if brokers == None:
            flash("No brokers attached!!!", "info")
        
        
        return render_template('my_brokers.html',brokers = brokers)
    
