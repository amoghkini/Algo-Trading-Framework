from flask import flash, redirect, url_for, render_template
from flask.views import MethodView

from exceptions.api_exceptions import APIException
from exceptions.user_exceptions import UserSignatureError
from user.user_status import UserStatus
from user.user_methods import UserMethods   

class VerifyUserAPI(MethodView):
    
    def get(self, token):
        try:
            email_id: str = UserMethods.decode_token(token)
            if not email_id:
                raise UserSignatureError('The account verification link is either expired or invalid. Please login to verify the account.')

            UserMethods.change_account_status(email_id, UserStatus.ACTIVATED)
            flash("Account activated successfully!!!", "success")
            return redirect(url_for('login_api'))

        except APIException as e:
            flash(str(e), 'danger')
            return redirect(url_for('login_api'))
        except UserSignatureError as e:
            flash(str(e), 'danger')
            return redirect(url_for('login_api'))
        except Exception as e:
            flash("Something went wrong while verifying the user. Please try after sometime.", 'danger')
            return redirect(url_for('login_api'))