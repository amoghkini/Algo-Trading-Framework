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
        """
        Adds a new user to the 'users' database table with the given user data.

        Args:
            user_data (dict): A dictionary containing the data for the new user.
                The dictionary should have the following keys:
                - 'first_name' (str): The first name of the user.
                - 'last_name' (str): The last name of the user.
                - 'email_id' (str): The email address of the user.
                - 'password' (str): The password of the user.

        Returns:
            bool: True if the new user was successfully added to the database, False otherwise.

        Raises:
            Exception: If there was an error while adding the new user to the database.

        Example usage:
            user_data = {'first_name': 'John Doe', 'email_id': 'johndoe@example.com', 'password': 'Password@123'}
            added = add_new_user(user_data)
            if added:
                print("New user added successfully!")
            else:
                print("Failed to add new user.")
        """
        
        print(user_data)
        try:
            conn.insert("users", user_data)
            conn.commit()
            return True
        except Exception as e:
            print("Exception occured while adding new user",e)
        

    @staticmethod
    def fetch_one_user(email):
        """
        Fetches the user data for a given email from the 'users' database table.

        Args:
            email (str): The email address of the user to fetch.

        Returns:
            dict: A dictionary containing the user data for the given email.
                The dictionary has the following keys:
                - 'id' (int): The unique identifier of the user.
                - 'email_id' (str): The email address of the user.
                - 'password' (str): The password of the user.
                - 'user_name' (str): The name of the user.

                If no user is found with the given email, None is returned.

        Example usage:
            user_email = 'johndoe@example.com'
            user_data = fetch_one_user(user_email)
            if user_data:
                print(f"User with email '{user_email}' found. User data: {user_data}")
            else:
                print(f"No user found with email '{user_email}'.")
        """
        
        user = conn.getOne("users", ["id", "email_id", "password", "user_name"], ("email_id = %s", [email]))
        if user:
            return user
        else:
            return None
    
    @staticmethod        
    def fetch_one_user_by_username(username):
        """
        Fetches the user data for a given username from the 'users' database table.

        Args:
            username (str): The username of the user to fetch.

        Returns:
            dict: A dictionary containing the user data for the given username.
                The dictionary has the following keys:
                - 'id' (int): The unique identifier of the user.
                - 'email_id' (str): The email address of the user.
                - 'password' (str): The password of the user.
                - 'user_name' (str): The username of the user.

                If no user is found with the given username, None is returned.

        Example usage:
            username = 'johndoe'
            user_data = fetch_one_user_by_username(username)
            if user_data:
                print(f"User with username '{username}' found. User data: {user_data}")
            else:
                print(f"No user found with username '{username}'.")
        """
        
        user = conn.getOne("users", '*', ("user_name = %s", [username]))
        if user:
            return user
        else:
            return None
        
    @staticmethod
    def check_if_user_is_already_registered(email):
        """
        Checks if a user with a given email address is already registered in the 'users' database table.

        Args:
            email (str): The email address to check.

        Returns:
            int: Returns 1 if a user with the given email address is already registered, 0 otherwise.

        Example usage:
            user_email = 'johndoe@example.com'
            is_registered = check_if_user_is_already_registered(user_email)
            if is_registered:
                print(f"User with email '{user_email}' is already registered.")
            else:
                print(f"No user found with email '{user_email}'.")
        """
        
        user = conn.getOne("users", ["email_id"], ("email_id = %s", [email]))
        print("User", user)
        if user:
            return 1
        return 0

    @staticmethod
    def validate_user_login(user, email, password):
        """
        Validates a user's login credentials against the provided email and password.

        Args:
            user (dict): A dictionary containing the user data for the provided email.
                The dictionary has the following keys:
                - 'email_id' (str): The email address of the user.
                - 'password' (str): The hashed password of the user.

            email (str): The email address provided by the user during login.

            password (str): The password provided by the user during login.

        Returns:
            int: Returns 1 if the provided email and password match the user's credentials, 0 otherwise.

        Example usage:
            user_data = {'email_id': 'johndoe@example.com',
                'password': '$5$rounds=535000$.T1yH0FOevOuslGm$JBm63lRcgDEmET0QCVzs9iAIzJjKk4ENe1q3q8/CswB'}
            email = 'johndoe@example.com'
            password = 'mypassword'
            is_valid = validate_user_login(user_data, email, password)
            if is_valid:
                print(f"User with email '{email}' logged in successfully.")
            else:
                print("Invalid email or password.")
        """
    
        print("Result", user)
        if (user.get('email_id') == email) and (sha256_crypt.verify(password, user.get('password'))):
            print("Logged in successfully!!!")
            return 1
        else:
            print("Invalid email or password")
            return 0

    @staticmethod
    def check_if_invalid_email(email):
        """Checks if the given email address is invalid.

        This function uses regular expressions to check if the given email address
        is valid or not. It returns 0 if the email address is valid, and 1 if it
        is invalid.

        Args:
            email (str): The email address to check.

        Returns:
            int: 0 if the email address is valid, 1 if it is invalid.
        """
        
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
        """Generates a unique username based on the given first and last names.

        This function generates a username by concatenating the first 5 characters of the
        first name (lowercased), an underscore, and the first character of the last name
        (lowercased). If the resulting username is longer than 8 characters, it is truncated
        to 8 characters. If the username already exists in the database, the function modifies
        it by appending characters from the first and last names or a count at the end until
        it finds a unique username.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.

        Returns:
            str: A unique username based on the given first and last names.
        """
    
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
        """Creates a secure hash of the given password.

        This function takes a password as input and uses the sha256_crypt algorithm
        to create a secure hash of the password. The resulting hash can be stored
        in a database to verify the password later.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The secure hash of the password.
        """
        
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
