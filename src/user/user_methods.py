import os
import re
import secrets
from flask import url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.exc import SignatureExpired
from passlib.hash import sha256_crypt
from PIL import Image
from typing import Dict

from database.database_connection import get_db
from exceptions.api_exceptions import APIException
from exceptions.user_exceptions import AuthUserError, InvalidUserDataError, UserNotFoundError, UserSignatureError
from messages.email import Email
from user.user import User
from utils.utils import Utils


class UserMethods:
    
    @staticmethod
    def activate_account(email_id: str) -> None:
        # Generate account activation token.
        verify_token = UserMethods.generate_token(email_id)
        link = f'''Click here to verify the account: {url_for('verify_email_api', token=verify_token, _external=True)}'''

        # Send acccount activation link to given email address.
        Email.send_account_activation_email(link)

    
    @staticmethod
    def add_new_user(user: User) -> None:
        try:
            conn = get_db()
            user_dict = user.__dict__
            conn.insert("users", user_dict)
            conn.commit()

            # Need to handle exceptions such as handle duplicate entry. We need to send different error on screen.
        except Exception as e:
            print(e)
            raise ValueError("Something went wrong while writing the database. Please retry after sometime.")
    
    @staticmethod
    def change_account_status(email_id: str,
                              status: str) -> None:
        user = UserMethods.get_user(email_id)
        if user.get('account_status') == status:
            raise APIException(f"The account is already {status}")
        fields_to_update = {"account_status" : status}
        UserMethods.update_user_data(email_id, fields_to_update, by='email_id')
    
    @staticmethod
    def change_password(user: Dict,
                        reset: bool = False) -> None:
        UserMethods.validate_change_password(user, reset)
        hashed_password = UserMethods.hash_password(user.get('new_password'))
        print("Hashed password", hashed_password)
        fields_to_update = {"password": hashed_password}
        UserMethods.update_user_data(user.get('user_name'), fields_to_update)
    
    @staticmethod
    def check_if_old_and_new_password_is_same(user: Dict, 
                                              existing_user: Dict) -> bool:
        if user.get('new_password') == user.get('confirm_new_password'):
            if sha256_crypt.verify(user.get('old_password'), existing_user.get('password')):
                if user.get('old_password') == user.get('new_password'):
                    return True
                else:
                    return False
            else:
                raise InvalidUserDataError("Please enter the correct old password")
        else:
            raise InvalidUserDataError("The new password and confirm new password should be same.")
        
    @staticmethod
    def decode_token(token: str,
                     secret_key: str = 'secret_key') -> str:
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except SignatureExpired as e:
            raise UserSignatureError("The account activation link is expired. Please login to activate the account.")
        except:
            return None
        return user_id
    
    @staticmethod
    def generate_token(user_id: str,
                       secret_key: str = 'secret_key',
                       epires_sec: int = 1000) -> str:
        # need to figure out how to pass secret key. It can be from config file or env.# need to figure out how to pass secret key. It can be from config file or env.
        s = Serializer(secret_key, epires_sec)
        return s.dumps({'user_id': user_id}).decode('utf-8')

    @staticmethod
    def generate_user_name(first_name: str, 
                           last_name: str) -> str:

        # Generate the initial username
        username = f"{first_name[:5]}_{first_name[0]}{last_name[0]}".lower()

        # Check if the initial username already exists
        username_exists = UserMethods.get_user_by_username(username)

        # If the username already exists, modify it
        if username_exists:
            last_name_index = 1
            first_name_index = 0
            while username_exists:
                # If all characters of last name are used and the username still exists, reset the last name index and try using next character of first name
                if last_name_index >= len(last_name):
                    last_name_index = 0
                    first_name_index += 1

                    # If all characters of first name are also used, append count to the end of username
                    if first_name_index >= len(first_name):
                        count = 1
                        while True:
                            if count > 99:
                                raise ValueError("Could not find a unique username.")
                            if count < 10:
                                modified_username = f"{username[:-1]}{count}"
                            else:
                                modified_username = f"{username[:-2]}{count}"
                            if not UserMethods.get_user_by_username(modified_username):
                                return modified_username
                            count += 1
                    else:
                        username = f"{username[:6]}{first_name[first_name_index]}{last_name[0]}"
                        first_name_index += 1
                else:
                    username = f"{username[:7]}{last_name[last_name_index]}"
                    last_name_index += 1
                username_exists = UserMethods.get_user_by_username(username)
        return username

    @staticmethod
    def get_user(email: str) -> Dict:
        try:
            conn = get_db()
            user = conn.getOne("users", '*', ("email_id = %s", [email]))
            return user
        except Exception as e:
            raise ValueError("Something went wrong while fetching the user details.")

    @staticmethod
    def get_user_by_username(username: str) -> Dict:
        try:
            conn = get_db()
            user = conn.getOne("users", '*', ("user_name = %s", [username]))
            return user
        except Exception as e:
            raise ValueError("Something went wrong while checking if username exist.")

    @staticmethod
    def hash_password(password: str) -> str:
        secure_password = sha256_crypt.encrypt(str(password))
        return secure_password
    
    @staticmethod
    def login_user(user: Dict) -> Dict:
        existing_user = UserMethods.get_user(user.get('email_id'))
        if existing_user:
            status = UserMethods.validate_user_login(user, existing_user)
            if not status:
                raise AuthUserError("The entered email id or password is incorret")
        else:
            raise AuthUserError("The entered email id or password is incorret")
        return existing_user
    
    @staticmethod
    def request_reset_password(email_id: str) -> None:
        existing_user = UserMethods.get_user(email_id)
        if existing_user:
            # Generate password reset token.
            verify_token = UserMethods.generate_token(email_id)
            link = f'''Click here to verify the account: {url_for('reset_password_api', token=verify_token, _external=True)}'''

            # Send password reset link to given email address.
            Email.send_password_reset_email(link)
    
    @staticmethod
    def verify_password_reset_token(token: str):
        email_id = UserMethods.decode_token(token)
        user = UserMethods.get_user(email_id)
        if not user:
            raise UserNotFoundError("The password reset link is either expired or invalid. Please try to reset the account again.")
    
    @staticmethod
    def reset_password(user: Dict) -> Dict:
        UserMethods.change_password(user, reset=True)
    
    @staticmethod
    def sign_up_user(user: User) -> None:
        UserMethods.validate_user_sign_up(user)
        user.password = UserMethods.hash_password(user.password)
        UserMethods.add_new_user(user)
    
    @staticmethod
    def update_user_data(user_identifier: str,
                         fields_to_update: Dict,
                         by: str='user_name') -> int:
        
        conn = get_db()
        user = conn.update("users", fields_to_update, (by+"=%s", (user_identifier,))) 
        if user:
            conn.commit()
            return user
        else:
            return None
        
    @staticmethod
    def validate(data: str, regex: str) -> bool:
        """Custom Validator"""
        return True if re.match(regex, data) else False
    
    @staticmethod
    def validate_change_password(user: Dict,
                                 reset: bool) -> None:
        if reset:
            existing_user = UserMethods.get_user(user.get('email_id'))
        else:
            existing_user = UserMethods.get_user_by_username(user.get('user_name'))
            
        if not existing_user:
            raise InvalidUserDataError("The username with this email address is not registered.")

        if not reset:
            password_status = UserMethods.check_if_old_and_new_password_is_same(user, existing_user)
            if password_status:
                raise InvalidUserDataError("The old and new password should not be same.")
        password_status = UserMethods.validate_password(user.get('new_password'))
        if not password_status:
            raise InvalidUserDataError("Please enter the paswword that contains capital & small letters, numbers and characters.")
    
    @staticmethod
    def validate_user_login(user: Dict,
                            db_user_data: Dict) -> bool:
        if (user.get('email_id') == db_user_data.get('email_id')) and \
            (sha256_crypt.verify(user.get('password'),db_user_data.get('password'))):
            return True
        else:
            return False
            
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email Validator"""
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return UserMethods.validate(email, regex)
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Password Validator"""
        reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
        return UserMethods.validate(password, reg)

    @staticmethod
    def validate_user_sign_up(user: User) -> None:
        # Check if user already exist
        existing_user = UserMethods.get_user(user.email_id)
        if existing_user:
            raise UserNotFoundError("The username with this email address or phone is already exist. Please log in to the acount.")

        email_status = UserMethods.validate_email(user.email_id)
        if not email_status:
            raise InvalidUserDataError("Please enter the valid email address.")

        password_status = UserMethods.validate_password(user.password)
        if not password_status:
            raise InvalidUserDataError("Please enter the paswword that contains capital & small letters, numbers and characters.")

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

    @staticmethod
    def get_profile_data(form):
        user_name: str = form.username.data
        user_db_data: Dict = UserMethods.get_user_by_username(user_name)
        if not user_db_data:
            raise UserNotFoundError("The username with this email address is not registered.")
        print("Data from db fetched successfully")
        user_form = UserMethods.convert_dict_to_profile_form(form, user_db_data)
        return user_form
    
    @staticmethod
    def update_profile(form) -> None:
        user_form_data: Dict = UserMethods.convert_profile_form_to_dict(form)
        if len(user_form_data) == 0:
            raise APIException("Something went wrong. Please retry after sometime")
        email_id: str = user_form_data.get('email_id')
        user_db_data: Dict = UserMethods.get_user(email_id)
        if not user_db_data:
            raise UserNotFoundError("The username with this email address is not registered.")
        fields_to_update = Utils.get_mismatches_from_two_dict(user_form_data, user_db_data)
        
        # Check for profile pic changes
        if form.picture.data:
                picture_file = UserMethods.save_picture(form.picture.data)
                fields_to_update['profile_pic'] = picture_file
        print(fields_to_update)
        if len(fields_to_update) != 0 :
            status = UserMethods.update_user_data(email_id, fields_to_update, by='email_id')
            if status == 0:
                raise InvalidUserDataError("No changes found to update the profile details.")                
        else:
            raise InvalidUserDataError("No changes found to update the profile details.")
    
    @staticmethod
    def convert_profile_form_to_dict(form) -> Dict:
        try:
            user_form_data = dict()
            user_form_data['first_name'] =  form.first_name.data
            user_form_data['middle_name'] = form.middle_name.data
            user_form_data['last_name'] = form.last_name.data
            user_form_data['user_name'] = form.username.data
            user_form_data['email_id'] = form.email.data
            user_form_data['address1'] = form.address1.data
            user_form_data['address2'] = form.address2.data
            user_form_data['address3'] = form.address3.data
        except Exception as e:
            raise APIException("Something went wrong. Please retry after sometime")
        
        return user_form_data
    
    @staticmethod
    def convert_dict_to_profile_form(form, user: Dict):
        try:
            form.username.data = user.get('user_name')
            form.email.data = user.get('email_id')
            form.first_name.data = user.get('first_name')
            form.middle_name.data = user.get('middle_name')
            form.last_name.data = user.get('last_name')
            form.address1.data = user.get('address1')
            form.address2.data = user.get('address2')
            form.address3.data = user.get('address3')
            form.picture.data = user.get('profile_pic')
        except Exception as e:
            raise APIException("Something went wrong. Please retry after sometime")
        return form