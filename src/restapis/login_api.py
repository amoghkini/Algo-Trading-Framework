import logging
from typing import Dict
from flask import render_template, flash, redirect, url_for, session, g
from flask.views import MethodView

from exceptions.user_exceptions import AuthUserError
from forms.login_user_form import LoginForm
from user.user_methods import UserMethods
from user.user_status import UserStatus

class LogInAPI(MethodView):
    
    
    def get(self):
        # If status is Created, make sure user activates account before redireting to username.
        if g.user:
            return redirect(url_for('dashboard_api'))
        
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        try:
            session.pop('user', None)
            form = LoginForm()
            
            email_id: str = form.email.data
            password: str = form.password.data
            
            user: Dict = {"email_id": email_id,
                          "password": password}
            
            user_data: Dict = UserMethods.login_user(user)
            
            if user_data.get('account_status') == UserStatus.CREATED:
                # Activate account
                UserMethods.activate_account(email_id)
                flash('Account activation list sent on registered email address. Please activate account before login!!!', 'success')
                return redirect(url_for('login_api'))
            
            session['user'] = user_data.get('user_name')
            flash('Logged In Successfully!!!', 'success')
            return redirect(url_for('dashboard_api'))
        
        except AuthUserError as e:
            flash(str(e), 'danger')
            return render_template('login.html', form=form)
        except Exception as e:
            return render_template('login.html', form=form)