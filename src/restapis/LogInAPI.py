from flask import render_template, flash
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
        form = LoginForm()
        user = User()
        user.fetch_one_user(form)
        flash('Logged In Successfully', 'success')
        return render_template('dashboard.html')
