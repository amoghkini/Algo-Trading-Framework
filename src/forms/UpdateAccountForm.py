from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=40)])
    middle_name = StringField('Middle name', validators=[DataRequired(), Length(min=2, max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=40)], render_kw={"placeholder": "Last name"})
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    picture = FileField('Change Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    address1 = StringField('Address line 1', validators=[ DataRequired(), Length(min=2, max=40)])
    address2 = StringField('Address line 2', validators=[ DataRequired(), Length(min=2, max=40)])
    address3 = StringField('Address line 3', validators=[ DataRequired(), Length(min=2, max=40)])
    submit = SubmitField('Update Details')

    '''
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'This username is already taken. Please choose a different one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'This email is already taken. Please choose a different one')
    '''
