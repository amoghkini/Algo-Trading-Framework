from flask import flash, render_template, redirect, url_for
from flask.views import MethodView
from common.redirect_page import RedirectPage

class RdirectHandlerAPI(MethodView):

    def get(self, page_name):
        if page_name == RedirectPage.HOLDINGS:
            return render_template('holdings.html')
        elif page_name == RedirectPage.ORDERS:
            return render_template('orders.html')
        elif page_name == RedirectPage.POSITIONS:
            return render_template('positions.html')
        else:
            flash("Not able to redirect to requested page. Please try after sometime.",'info')
            return render_template('dashboard.html')
