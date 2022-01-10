from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FormField, RadioField, FieldList
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class QuizQuestionForm(FlaskForm):
    question_text = StringField("")
    radio_field = RadioField(validators=[DataRequired()])


class QuizForm(FlaskForm):
    questions = FieldList(FormField(QuizQuestionForm), min_entries=5)
    submit = SubmitField()


