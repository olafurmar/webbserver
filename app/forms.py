from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class TestScript(FlaskForm):
    args = StringField('Arguments for script', validators=[DataRequired()])
    submit = SubmitField('Run script')