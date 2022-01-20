from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, NumberRange
from users.forms import name_check


class CreateGroup(FlaskForm):
    name = StringField(validators=[InputRequired(), name_check])
    size = IntegerField(validators=[NumberRange(min=1, max=50)], default=30)
    key_stage = IntegerField(validators=[NumberRange(min=1, max=9)])
    submit = SubmitField()


class RegisterStudent(FlaskForm):
    names = TextAreaField(validators=[InputRequired(), name_check])
    submit = SubmitField()
