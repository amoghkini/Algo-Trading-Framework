from flask import render_template, flash, redirect, url_for
from flask.views import MethodView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from forms.LoginUser import LoginForm
from user.User import User
from models.UserModel import UserModel


class LogInAPI(MethodView):
    
    
    def get(self):
        print("Inside get method")
        if current_user.is_authenticated:
            return redirect(url_for("dashboard_api"))
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        print("Inside post method")
        if current_user.is_authenticated:
            return redirect(url_for("dashboard_api"))
        form = LoginForm()
        #user = User()
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
            print("USER",user   )
            user = UserModel(*user)
            print(user)
            login_user(user)
            return 1
        else:
            print("Invalid username or password")
                
            return 0    