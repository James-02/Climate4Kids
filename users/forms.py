from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, ValidationError, Length


def name_check(_form, name):
    chars = "* ? ! ' ^ + % & / ( ) = } ] [ { $ # @ < >"
    for char in name.data:
        if char in chars:
            raise ValidationError("Special Characters not allowed.")


class GroupRegistrationForm(FlaskForm):
    name = StringField(validators=[InputRequired(), name_check])
    size = IntegerField(validators=[Length(min=1, max=50)], default=50, message="Maximum group size is 50.")
