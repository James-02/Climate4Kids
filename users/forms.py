from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectMultipleField, widgets, RadioField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class QuizQuestion(FlaskForm):
    question = StringField("")
    radio_field = RadioField(validators=[DataRequired()])
    submit = SubmitField()
