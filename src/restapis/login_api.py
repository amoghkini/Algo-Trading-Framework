import logging
from flask import render_template, flash, redirect, url_for, session, g
from flask.views import MethodView

from forms.login_user_form import LoginForm
from user.user import User

class LogInAPI(MethodView):
    
    
    def get(self):
        if g.user:
            return redirect(url_for('dashboard_api'))
        
        print("Inside get method")
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        print("Inside post method")
        session.pop('user',None) # Drop the session if already exist
        
        form = LoginForm()
        
        result = User.fetch_one_user(form.email.data)
        if not result:
            flash('The entered email id or password is incorrect!!!','danger')
            return render_template('login.html', form=form)
        
        
        validation_result = User.validate_user_login(result, form.email.data, form.password.data)
        
        if validation_result:
            logging.info("Logged in successfuly!!!")
            session['user'] = result.get('user_name')
            flash('Logged In Successfully!!!', 'success')
        else:
            flash('The entered email id or password is incorrect!!!', 'danger')
            return render_template('login.html', form=form)
        return redirect(url_for('dashboard_api'))
