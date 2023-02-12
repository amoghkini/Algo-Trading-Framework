from flask import flash, redirect, render_template, url_for
from flask.views import MethodView

from forms.ResetPassword import ResetPasswordForm


class ResetPasswordAPI(MethodView):
    def get(self):
        print("Inside get method")
        form = ResetPasswordForm()
        return render_template('reset_token.html', form=form)
