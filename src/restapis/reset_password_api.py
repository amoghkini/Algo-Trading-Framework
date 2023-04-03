from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView

from forms.reset_password_form import ResetPasswordForm
from user.user import User


class ResetPasswordAPI(MethodView):
    def get(self, token):
        if g.user:
            return redirect(url_for('dashboard_api'))
                
        user_name = User.decode_reset_token(token, g.secret_key)
        
        user = User.fetch_one_user_by_username(user_name)
        if not user:
            flash('The password reset link is either expired or invalid. Please reset the password again.', 'warning')
            return redirect(url_for('reset_password_request_api'))
        
        form = ResetPasswordForm()
        return render_template('reset_password.html', form=form)


    def post(self,token):
        if g.user:
            return redirect(url_for('dashboard_api'))

        user_name = User.decode_reset_token(token, g.secret_key)

        user = User.fetch_one_user_by_username(user_name)
        if not user:
            flash('The password reset link is either expired or invalid. Please reset the password again.', 'warning')
            return redirect(url_for('reset_password_request_api'))

        form = ResetPasswordForm()
        
        error, flash_message = self.validate_password_reset(form,user.get('password'))
        if error:
            flash(flash_message, "danger")
            return render_template('reset_password.html', form=form)
        
        user = User.update_password_reset_data(form.password.data, user_name)
        print(user)
        
        flash('Your password has been updated successfully! You can now log in to the system.', 'success')
        return redirect(url_for('login_api'))
    
    
    def validate_password_reset(self,form, old_password):
        error = 0

        result = User.validate_pass_and_confirm_pass(form.password.data, form.confirm_password.data)
        if result:
            error = 1
            flash_message = "The password and confirm password should be same"
            return error, flash_message

        result = User.validate_if_new_password_is_same_as_old(old_password, form.password.data)
        if not result:
            error = 1
            flash_message = "The old and new password is same. Please provide the different password."
            return error, flash_message
        
        result = User.check_if_not_following_password_rules(form.password.data)
        if result:
            error = 1
            flash_message = "The password should be at least eight characters, contains at least one number and both lower and uppercase letters and special characters"
            return error, flash_message

        return 0, ''
