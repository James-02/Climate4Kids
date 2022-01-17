from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, InputRequired, ValidationError, NumberRange, equal_to


def name_check(_form, name):
    chars = ["*", "?", "!", "'", "^", "+", "%", "&", "/", "(", ")",
             "=", "}", "]", "[", "{", "$", "#", "@", "<", ">", '"']
    for char in name.data:
        if char in chars:
            flash("Special characters are not allowed", "danger")
            raise ValidationError("Name cannot include special characters.")


class CreateGroup(FlaskForm):
    name = StringField(validators=[InputRequired(), name_check])
    size = IntegerField(validators=[NumberRange(min=1, max=50)], default=30)
    key_stage = IntegerField(validators=[NumberRange(min=1, max=9)])
    submit = SubmitField()


class RegisterStudent(FlaskForm):
    names = TextAreaField(validators=[InputRequired(), name_check])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), name_check])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class ChangePassword(FlaskForm):
    username = StringField(validators=[DataRequired(), name_check])
    current_password = PasswordField(validators=[DataRequired()])
    new_password = PasswordField(validators=[DataRequired()])
    confirm_new_password = PasswordField(
        validators=[DataRequired(), equal_to('new_password', message="Passwords must match")])
    submit = SubmitField()
