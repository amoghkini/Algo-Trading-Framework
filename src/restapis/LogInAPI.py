from flask import render_template, flash, redirect, url_for, session, g
from flask.views import MethodView
from forms.LoginUser import LoginForm
from user.User import User

class LogInAPI(MethodView):
    
    
    def get(self):
        print("Inside get method")
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        print("Inside post method")
        session.pop('user',None) # Drop the session if already exist
        
        form = LoginForm()
        result = User.fetch_one_user(form)
        if not result:
            flash('User not found!!!')
            print("User not found")
            return redirect(url_for('login_api'))
        result = self.validate_user_login(result,form)
        if result:
            flash('Logged In Successfully', 'success')
        else:
            flash('Invalid userid or password!!!')
            return redirect(url_for('login_api'))
        return render_template('dashboard.html')


    def validate_user_login(self, user, form):
        print("Result", user)
        if (user.get('email') == form.email.data) and (user.get('password') == form.password.data):
            print("Logged in successfully!!!")
            session['user'] = form.email.data
            return 1
        else:
            print("Invalid username or password")
                
            return 0    