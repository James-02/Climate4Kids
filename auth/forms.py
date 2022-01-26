import re
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from users.forms import name_check


class RegisterForm(FlaskForm):
    # Adds validation to the user inputs
    username = StringField(validators=[DataRequired(), name_check])
    email = StringField(validators=[DataRequired(), Email()])
    fullname = StringField(validators=[DataRequired(), name_check])
    password = PasswordField(validators=[DataRequired(), Length(min=10, max=99)])
    repeatpassword = PasswordField(validators=[DataRequired()])
    submit = SubmitField()

    def validate_password(self, _password):
        # Function makes sure the password contains certain characters to ensure strength
        inputpass = re.compile(r'(?=.*[A-Z])(?=.*[*?!()^+%&/$#@<>=}{~£])(?=.*\d)')
        if not inputpass.match(self.password.data):
            flash("Password requires at least 1 digit, 1 uppercase letter and 1 special character.", 'danger')
            raise ValidationError("Password requires at least 1 digit, 1 uppercase letter and 1 special character.")


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), name_check])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()
