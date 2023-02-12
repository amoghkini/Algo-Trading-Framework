from flask import flash, redirect, render_template, url_for
from flask.views import MethodView

from forms.ResetPassword import RequestResetForm


class RequestPassResetAPI(MethodView):
    def get(self):
        print("Inside get method")
        form = RequestResetForm()
        return render_template('reset_request.html', form=form)
