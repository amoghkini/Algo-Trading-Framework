from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView
from passlib.hash import sha256_crypt

from forms.ChangePasswordForm import ChangePasswordForm
from user.User import User


class ChangePasswordAPI(MethodView):
    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        '''
        user_name = User.decode_reset_token(token, g.secret_key)

        user = User.fetch_one_user_by_username(user_name)
        if not user:
            flash('The password reset link is either expired or invalid. Please reset the password again.', 'warning')
            return redirect(url_for('reset_password_request_api'))
        '''
        form = ChangePasswordForm()
        return render_template('change_password.html', form=form)

    def post(self):
        if not g.user:
            return redirect(url_for('login_api'))

        user = User.fetch_one_user_by_username(g.user)
        if not user:
            flash('Something went wrong. Please try again after sometime.', 'warning')
            return redirect(url_for('reset_password_request_api'))

        form = ChangePasswordForm()

        if not (sha256_crypt.verify(form.old_password.data, user.get('password'))):
            flash("Please enter the correct old password","danger")
            return render_template('change_password.html', form=form)
        
        
        error, flash_message = self.validate_password_change(form)
        if error:
            flash(flash_message, "danger")
            return render_template('change_password.html', form=form)

        user = User.update_password_reset_data(form.new_password.data, g.user)
        print(user)

        flash('Your password has been updated successfully!!!', 'success')
        return redirect(url_for('dashboard_api'))

    def validate_password_change(self, form):
        error = 0

        result = User.validate_pass_and_confirm_pass(form.new_password.data, form.confirm_new_password.data)
        if result:
            error = 1
            flash_message = "The password and confirm password should be same"
            return error, flash_message

        result = User.validate_if_new_password_is_same_as_old(form.old_password.data, form.new_password.data)
        if not result:
            error = 1
            flash_message = "The old and new password is same. Please provide the different password."
            return error, flash_message

        result = User.check_if_not_following_password_rules(form.new_password.data)
        if result:
            error = 1
            flash_message = "The password should be at least eight characters, contains at least one number and both lower and uppercase letters and special characters"
            return error, flash_message

        return 0, ''
