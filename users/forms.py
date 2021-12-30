from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, NumberRange


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
