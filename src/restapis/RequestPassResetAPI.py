from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView

from forms.ResetPassword import RequestResetForm
from user.User import User

class RequestPassResetAPI(MethodView):
    def get(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        print("Inside get method")
        form = RequestResetForm()
        return render_template('reset_request.html', form=form)

    def post(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        
        form = RequestResetForm()
        result = User.fetch_one_user(form.email.data)
        if result:
            reset_token = User.get_reset_token(result.get('user_name'), g.secret_key)
            link = f'''Click here to reset the password: {url_for('reset_password_api', token=reset_token, _external=True)}'''
            print("Link",link)
        flash("The password reset link has been sent successfully on registered email address","success")
        return redirect(url_for('login_api'))