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
