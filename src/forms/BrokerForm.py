from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from database.DatabaseConnection import conn


class BrokerForm(FlaskForm):
    broker_name = SelectField('Select Broker', choices = ['Zerodha'], validators=[DataRequired()])
    user_id = StringField('User ID', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    totp_key = StringField('TOTP key', validators=[DataRequired(), Length(min=32, max=32)])

    submit = SubmitField('Add Broker')
