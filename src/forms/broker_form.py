from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms_components import read_only
from wtforms.validators import DataRequired, Length

from broker.brokers import Brokers

class BrokerCreateForm(FlaskForm):
    broker_name = SelectField('Select Broker', choices = [Brokers.ZERODHA], validators=[DataRequired()])
    broker_id = StringField('Broker ID', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    app_key = StringField('App key', validators=[Length(min=1, max=32)])
    app_secret_key = StringField('App secret key', validators=[Length(min=1, max=32)])
    totp_key = StringField('TOTP key', validators=[DataRequired(), Length(min=32, max=32)])
    auto_login = SelectField('Auto Login', choices=["Yes","No"], validators=[DataRequired()])
    submit = SubmitField('Add Broker')


class BrokerEnquiryForm(FlaskForm):
    broker_name = SelectField('Select Broker', choices=[Brokers.ZERODHA], validators=[DataRequired()])
    broker_id = StringField('Broker ID', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    app_key = StringField('App key', validators=[Length(min=1, max=32)])
    app_secret_key = StringField('App secret key', validators=[Length(min=1, max=32)])
    totp_key = StringField('TOTP key', validators=[DataRequired(), Length(min=32, max=32)])
    submit = SubmitField('Add Broker')

class BrokerLoginForm(FlaskForm):
    
    broker_name = SelectField('Broker Name', choices=[Brokers.ZERODHA], validators=[DataRequired()], render_kw={'readonly': True})
    broker_id = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={'readonly': True})
    password = PasswordField('Password', validators=[DataRequired()])
    login_method = HiddenField('Login Method', validators=[DataRequired()])
    enc_token = StringField('Encryption Token', validators=[DataRequired(), Length(min=5, max=150)])
    submit = SubmitField('Login Broker')
    
    #def __init__(self, *args, **kwargs):
    #    super(BrokerLoginForm, self).__init__(*args, **kwargs)
    #    read_only(self.broker_name)
