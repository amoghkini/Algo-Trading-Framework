from flask_wtf import FlaskForm
from wtforms import  PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[ DataRequired()])
    submit = SubmitField('Change Password')
