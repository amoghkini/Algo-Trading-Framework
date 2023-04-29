from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView
from typing import Dict

from exceptions.user_exceptions import InvalidUserDataError
from forms.change_password_form import ChangePasswordForm
from user.user_methods import UserMethods


class PasswordChangeAPI(MethodView):
    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        form = ChangePasswordForm()
        return render_template('change_password.html', form=form)

    def post(self):
        if not g.user:
            return redirect(url_for('login_api'))
        try:
            form = ChangePasswordForm()
            print("User",g.user)
            user: Dict = {
                "user_name" : g.user,
                "old_password": form.old_password.data,
                "new_password": form.new_password.data,
                "confirm_new_password": form.confirm_new_password.data
            }
            
            UserMethods.change_password(user)
            flash("Password changed successfully!!!",'success')
            return redirect(url_for('my_profile_api'))
        
        except InvalidUserDataError as e:
            flash(str(e),'danger')
            return redirect(url_for('change_password_api'))
        except Exception as e:
            print("Exception",e)
            flash('Something went wrong. Please try again after sometime.', 'danger')
            return redirect(url_for('change_password_api'))