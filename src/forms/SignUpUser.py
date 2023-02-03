from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional


class RegisterUserForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "First name"})
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Last name"})
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    '''
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'This username is already taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError(
                'This email is already taken. Please choose a different one')
    '''