import re

from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FormField, RadioField, \
    FieldList
from wtforms.validators import DataRequired, ValidationError, Length, Email


def name_check(_form, name):
    chars = ["*", "?", "!", "'", "^", "+", "%", "&", "/", "(", ")",
             "=", "}", "]", "[", "{", "$", "#", "@", "<", ">", '"']
    for char in name.data:
        if char in chars:
            flash("Special characters are not allowed.", "danger")
            raise ValidationError("Name cannot include special characters.")


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


class ChangePassword(FlaskForm):
    username = StringField(validators=[DataRequired(), name_check])
    current_password = PasswordField(validators=[DataRequired()])
    new_password = PasswordField(validators=[DataRequired(), Length(min=10, max=99)])
    confirm_new_password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class QuizQuestionForm(FlaskForm):
    question_text = StringField("")
    radio_field = RadioField(validators=[DataRequired()])


class QuizForm(FlaskForm):
    questions = FieldList(FormField(QuizQuestionForm), min_entries=5)
    submit = SubmitField()


class ForgottenPassword(FlaskForm):
    username = StringField(validators=[DataRequired(), name_check])
    submit = SubmitField()
