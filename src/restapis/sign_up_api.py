from flask import flash, redirect, render_template, url_for, g
from flask.views import MethodView

from exceptions.user_exceptions import InvalidUserDataError, UserNotFoundError
from forms.sign_up_user_form import RegisterUserForm
from user.user import User
from user.user_methods import UserMethods

class SignUpAPI(MethodView):
    def get(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        form = RegisterUserForm()
        return render_template('signup.html', form=form)

    def post(self):
        try:
            form = RegisterUserForm()
            
            first_name: str = form.first_name.data
            last_name: str = form.last_name.data
            
            user = User(first_name, last_name)
            user.email_id = form.email.data
            user.password = form.password.data
            user.user_name = UserMethods.generate_user_name(first_name, last_name)
            user.mobile_no = form.mobile_no.data
            user.date_of_birth = form.date_of_birth.data
            # Perform user sign up
            UserMethods.sign_up_user(user)
            
            # Activate account
            UserMethods.activate_account(user.email_id)
            
            flash('The account activation mail has been sent to registerd email address!', 'success')
            return redirect(url_for('login_api'))
        
        except InvalidUserDataError as e:
            flash(str(e), 'danger')
            return render_template('signup.html', form=form)
        except UserNotFoundError as e:
            flash(str(e), 'danger')
            return render_template('signup.html', form=form)
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('signup.html', form=form)
        except Exception as e:
            flash("Something went wrong while creating the user. Please try after sometime.", 'danger')
            return render_template('signup.html', form=form)