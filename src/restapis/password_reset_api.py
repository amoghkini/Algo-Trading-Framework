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