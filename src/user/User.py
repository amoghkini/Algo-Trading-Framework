import os
import re
import secrets

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.hash import sha256_crypt
from PIL import Image


from database.DatabaseConnection import conn

class User:
    
    @staticmethod
    def add_new_user(user_data):
        print(user_data)
        try:
            conn.insert("users", user_data)
            conn.commit()
            return True
        except Exception as e:
            print("Exception occured while adding new user",e)
        

    @staticmethod
    def fetch_one_user(email):
        user = conn.getOne("users", ["id", "email_id", "password", "user_name"], ("email_id = %s", [email]))
        if user:
            return user
        else:
            return None
    
    @staticmethod        
    def fetch_one_user_by_username(username):
        user = conn.getOne("users", '*', ("user_name = %s", [username]))
        if user:
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
    def validate_user_login(user, email, password):
        print("Result", user)
        if (user.get('email_id') == email) and (sha256_crypt.verify(password, user.get('password'))):
            print("Logged in successfully!!!")
            return 1
        else:
            print("Invalid email or password")
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
    def validate_pass_and_confirm_pass(password: str, confirm_password: str):
        if password == confirm_password:
            return 0
        return 1

    @staticmethod
    def validate_if_new_password_is_same_as_old(old_password: str, new_password:str):
        '''
        This method checks if old and new passwords are same. This method internally calls validate_pass_and_confirm_pass for code reusability.
        '''
        return User.validate_pass_and_confirm_pass(old_password, new_password)
 
    
    
    @staticmethod
    def generate_user_name(first_name,last_name):
        '''
        username = first_name[:5].lower() + '_' + first_name[0].lower() + last_name[0].lower()
        if len(username) > 8:
            username = username[:8]
            
        '''
        # Generate the initial username
        username = f"{first_name[:5]}_{first_name[0]}{last_name[0]}".lower()
        
        # Check if the initial username already exists
        username_exists = User.fetch_one_user_by_username(username)
        
        # If the username already exists, modify it
        if username_exists:
            last_name_index = 1
            while username_exists:
                # If all characters of last name are used and the username still exists, reset the last name index and try using next character of first name
                if last_name_index >= len(last_name):
                    last_name_index = 0
                    first_name_index = len(username) - 2
                    # If all characters of first name are also used, append count to the end of username
                    if first_name_index >= len(first_name):
                        count = 1
                        while True:
                            if count > 99:
                                raise ValueError(
                                    "Could not find a unique username.")
                            if count < 10:
                                modified_username = f"{username[:-1]}{count}"
                            else:
                                modified_username = f"{username[:-2]}{count}"
                            if not User.fetch_one_user_by_username(modified_username):
                                return modified_username
                            count += 1
                    else:
                        username = f"{username[:6]}{first_name[first_name_index]}{last_name[0]}"
                        first_name_index += 1
                else:
                    username = f"{username[:7]}{last_name[last_name_index]}"
                    last_name_index += 1
                username_exists = User.fetch_one_user_by_username(username)
    
        return username
    
    @staticmethod
    def get_reset_token(user_id, secret_key, epires_sec = 1800):
        s = Serializer(secret_key, epires_sec) # need to figure out how to pass secret key. It can be from config file or env.# need to figure out how to pass secret key. It can be from config file or env.
        return s.dumps({'user_id':user_id}).decode('utf-8') 
    
    @staticmethod
    def decode_reset_token(token, secret_key):
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id

    @staticmethod
    def make_user_password_hash(password):
        secure_password = sha256_crypt.encrypt(str(password))
        return secure_password
    
    @staticmethod
    def update_password_reset_data(password,username):
        hashed_password = User.make_user_password_hash(password)
        fields_to_update = {"password": hashed_password}
        user = User.update_user_data(username,fields_to_update)
        return user
        
    @staticmethod
    def update_user_data(username,fields_to_update):
        print("Fields",fields_to_update)
        user = conn.update("users", fields_to_update, ("user_name=%s", (username,))) 
        print("User",user)
        if user:
            print("Amogh is here")
            conn.commit()
            return user
        else:
            return None
    
    @staticmethod
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        print("Form picture",form_picture)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(os.getcwd()  , 'static/profile_pic', picture_fn)  # Instead of os.getcwd() we should use app.root_path. This can be fetched from config file
        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        
        return picture_fn
