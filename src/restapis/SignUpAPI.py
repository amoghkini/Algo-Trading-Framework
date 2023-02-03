from flask import render_template, request, flash, redirect, url_for
from flask.views import MethodView
from forms.SignUpUser import RegisterUserForm
from user.User import User

class SignUpAPI(MethodView):
    def get(self):
        print("Inside get method")
        form = RegisterUserForm()
        return render_template('signup.html', form=form)

    def post(self):
        print("Amogh inside the post method")
        form = RegisterUserForm()
        user = User()
        user.add_new_user(form)
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login_api'))
    
    
