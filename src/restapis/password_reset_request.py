from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView

from forms.reset_password_form import RequestResetForm
from user.user_methods import UserMethods

class PasswordResetRequestAPI(MethodView):
    def get(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        form = RequestResetForm()
        return render_template('reset_request.html', form=form)

    def post(self):
        try:
            if g.user:
                return redirect(url_for('dashboard_api'))
            form = RequestResetForm()
            
            email_id: str = form.email.data
            UserMethods.request_reset_password(email_id)
            
            flash("The password reset link has been sent successfully on registered email address", "success")
            return redirect(url_for('login_api'))
        
        except Exception as e:
            flash('Something went wrong. Please try again after sometime.', 'danger')
            return render_template('reset_request.html', form=form)