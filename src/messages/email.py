class Email:

    @staticmethod
    def send_account_activation_email(verification_link: str):
        # This is just a temp solution. We can write the logic to send the email here.
        print("The account activation email has been sent", verification_link)

    @staticmethod
    def send_password_reset_email(activation_link: str):
        # This is just a temp solution. We can write the logic to send the email here.
        print("The password reset email has been sent", activation_link)