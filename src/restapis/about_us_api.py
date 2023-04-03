from flask import render_template
from flask.views import MethodView


class AboutUsAPI(MethodView):

    def get(self):
        return render_template('about_us.html')
