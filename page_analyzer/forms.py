from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL
from flask_wtf.csrf import CSRFProtect


class URLForm(FlaskForm):
    url = StringField('URL', validators=[URL()])
    submit = SubmitField('Submit')
    csrf_token = CSRFProtect()
