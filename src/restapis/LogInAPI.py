from flask import render_template, flash, redirect, url_for, session, g
from flask.views import MethodView

from forms.LoginUser import LoginForm
from user.User import User

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
        result = User.fetch_one_user(form)
        if not result:
            flash('The entered email id or password is incorrect!!!','danger')
            return redirect(url_for('login_api'))
        
        
        result = User.validate_user_login(result, form.email.data, form.password.data)
        
        if result:
            session['user'] = form.email.data
            flash('Logged In Successfully', 'success')
        else:
            flash('Invalid userid or password!!!')
            return redirect(url_for('login_api'))
        return redirect(url_for('dashboard_api'))
