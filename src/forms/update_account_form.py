from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=40)])
    middle_name = StringField('Middle name', validators=[DataRequired(), Length(min=2, max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=40)], render_kw={"placeholder": "Last name"})
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    picture = FileField('Change Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    address1 = StringField('Address line 1', validators=[Length(min=2, max=40)])
    address2 = StringField('Address line 2', validators=[Length(min=2, max=40)])
    address3 = StringField('Address line 3', validators=[Length(min=2, max=40)])
    submit = SubmitField('Update Details')