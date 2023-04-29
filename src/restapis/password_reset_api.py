from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView
from typing import Dict

from exceptions.user_exceptions import InvalidUserDataError, UserNotFoundError, UserSignatureError
from forms.reset_password_form import ResetPasswordForm
from user.user_methods import UserMethods


class PasswordResetAPI(MethodView):
    def get(self, token):
        try:
            if g.user:
                return redirect(url_for('dashboard_api'))
            
            UserMethods.verify_password_reset_token(token)
            
            form = ResetPasswordForm()
            return render_template('reset_password.html', form=form)
        
        except UserNotFoundError as e:
            flash(str(e), 'danger')
            return redirect(url_for('login_api'))
        except UserSignatureError as e:
            flash(str(e), 'danger')
            return redirect(url_for('login_api'))
        except Exception as e:
            flash("Something went wrong while reseting the password.", 'danger')
            return redirect(url_for('login_api'))

    def post(self, token):
        try:
            if g.user:
                return redirect(url_for('dashboard_api'))

            form = ResetPasswordForm()
            
            email_id: str = UserMethods.decode_token(token)
            user: Dict = {"email_id": email_id,
                          "new_password": form.password.data,
                          "confirm_new_password": form.confirm_password.data}
            
            UserMethods.reset_password(user)
            flash("Passoword changed successfully","success")
            return redirect(url_for('login_api'))
        
        except InvalidUserDataError as e:
            flash(str(e), 'danger')
            return render_template('reset_password.html', form=form)
        except UserSignatureError as e:
            flash(str(e), 'danger')
            return render_template('reset_password.html', form=form)
        except Exception as e:
            print(e)
            flash("Something went wrong resetting the password. Please try after sometime.", 'danger')
            return render_template('reset_password.html', form=form)
    
    # def post(self,token):
    #     if g.user:
    #         return redirect(url_for('dashboard_api'))

    #     user_name = UserMethods.decode_reset_token(token, g.secret_key)

    #     user = UserMethods.fetch_one_user_by_username(user_name)
    #     if not user:
    #         flash('The password reset link is either expired or invalid. Please reset the password again.', 'warning')
    #         return redirect(url_for('reset_password_request_api'))

    #     form = ResetPasswordForm()
        
    #     error, flash_message = self.validate_password_reset(form,user.get('password'))
    #     if error:
    #         flash(flash_message, "danger")
    #         return render_template('reset_password.html', form=form)
        
    #     user = UserMethods.update_password_reset_data(form.password.data, user_name)
    #     print(user)
        
    #     flash('Your password has been updated successfully! You can now log in to the system.', 'success')
    #     return redirect(url_for('login_api'))
    
    
    # def validate_password_reset(self,form, old_password):
    #     error = 0

    #     result = UserMethods.validate_pass_and_confirm_pass(form.password.data, form.confirm_password.data)
    #     if result:
    #         error = 1
    #         flash_message = "The password and confirm password should be same"
    #         return error, flash_message

    #     result = UserMethods.validate_if_new_password_is_same_as_old(old_password, form.password.data)
    #     if not result:
    #         error = 1
    #         flash_message = "The old and new password is same. Please provide the different password."
    #         return error, flash_message
        
    #     result = UserMethods.check_if_not_following_password_rules(form.password.data)
    #     if result:
    #         error = 1
    #         flash_message = "The password should be at least eight characters, contains at least one number and both lower and uppercase letters and special characters"
    #         return error, flash_message

    #     return 0, ''
