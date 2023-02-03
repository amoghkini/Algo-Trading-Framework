from flask import render_template, request
from flask.views import MethodView
from forms.ResetPassword import ResetPasswordForm


class ResetPasswordAPI(MethodView):
    def get(self):
        print("Inside get method")
        form = ResetPasswordForm()
        return render_template('reset_token.html', form=form)
