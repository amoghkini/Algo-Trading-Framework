import os
import smtplib


class Email:

    @staticmethod
    def send_mail(payload) -> None:        
        my_mail = os.environ.get('EMAIL')
        passcode = os.environ.get('EMAILPASS')

        connection = smtplib.SMTP("smtp.gmail.com")
        connection.starttls()  # transfer layer security
        connection.login(user=my_mail, password=passcode)
        
        mail_content = "Subject: {0} \n\n {1}".format(
            payload.get('subject'), payload.get("message"))

        try:
            connection.sendmail(from_addr=my_mail,to_addrs=payload.get('to'), msg=mail_content)  
            print("Mail sent successfully")  
        except Exception as e:
            print("Something went wrong while sending the mail", e)
        connection.close()