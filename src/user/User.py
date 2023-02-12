import re
from passlib.hash import sha256_crypt

from common.AccountStatus import AccountStatus
from database.DatabaseConnection import conn

class User:
    
    @staticmethod
    def add_new_user(form):
        conn.insert("users", {"first_name": form.first_name.data,
                              "last_name" : form.last_name.data,
                              "user_id" : 1,
                              "account_creation_date" : 4545,
                              "account_status" : AccountStatus.CREATED,
                              "mobile_no" : form.mobile_no.data,
                              "date_of_birth": 6565,
                              "email_id": form.email.data,
                              "password": form.password.data})
        conn.commit()
        return True

    @staticmethod
    def fetch_one_user(form):
        user = conn.getOne("users", ["id", "email_id", "password"], ("email_id = %s", [form.email.data]))
        if user:
            print("User found",user)
            return user
        else:
            return None
            

    @staticmethod
    def check_if_user_is_already_registered(email):
        user = conn.getOne("users", ["email_id"], ("email_id = %s", [email]))
        print("User", user)
        if user:
            return 1
        return 0

    @staticmethod
    def validate_user_login(user, username, password):
        print("Result", user)
        if (user.get('email_id') == username) and (sha256_crypt.verify(password, user.get('password'))):
            print("Logged in successfully!!!")
            return 1
        else:
            print("Invalid username or password")
            return 0

    @staticmethod
    def check_if_invalid_email(email):
        #refer:https://www.w3schools.com/python/python_regex.asp for regex syntax
        # https://docs.python.org/2/library/re.html
        
        res = re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email, re.IGNORECASE)
        if res:
            return 0
        else:
            return 1
        
    
    @staticmethod
    def check_if_not_following_password_rules(password):
        # To be implemented. The validation should be done using regex.
        #if len(password) < 8:
        #    return 1
        
        return 0
    
    
    @staticmethod
    def check_if_invalid_phone_number_format(number):
        # To be implemented. The validation should be done using regex.
        #if len(str(number)) < 10:
        #    return 1
        return 0
    
    @staticmethod
    def validate_pass_and_confirm_pass(password, confirm_password):
        if password == confirm_password:
            return 0
        return 1
