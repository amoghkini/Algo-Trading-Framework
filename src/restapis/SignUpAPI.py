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

        error, flash_message = self.validate_user_sign_up(form)
        if error:
            flash(flash_message,"danger")
            return render_template('signup.html',form=form)
        
        hashed_password = self.make_password_hash(form.password.data)
        form.password.data = hashed_password
                
        User.add_new_user(form)
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login_api'))
    
    
    def validate_user_sign_up(self,form):
        error = 0  
        
        result = User.check_if_invalid_email(form.email.data)
        if result:
            error = 1
            flash_message = "Please enter the valid email address!!!"
            return error, flash_message
        
        result = User.check_if_user_is_already_registered(form.email.data)
        if result:
            error = 1
            flash_message = "The email ID is already taken. Please use different one or use this email to login into the system!!!"
            return error, flash_message
        
        result = User.validate_pass_and_confirm_pass(form.password.data, form.confirm_password.data)
        if result:
            print("Incorrect password and confirm password")
            error = 1 
            flash_message = "The password and confirm password should be same"
            return error, flash_message
        
        result = User.check_if_not_following_password_rules(form.password.data)
        if result:
            print("The password should be at least eight characters, at least one number and both lower and uppercase letters and special characters")
            error = 1
            flash_message = "The password should be at least eight characters, at least one number and both lower and uppercase letters and special characters"
            return error, flash_message
        
        result = User.check_if_invalid_phone_number_format(form.mobile_no.data)
        if result:
            print("Please provide the valid phone number")
            error = 1
            flash_message = "Please provide the valid phone number"
            return error, flash_message
        
        return 0, ''

    
    def make_password_hash(self,password):
        return password
    