from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError
import app.models


class Add_Card(FlaskForm):
    def Cards(form, field):
        card = StringField('Name', validators=[DataRequired()])
        rarity = SelectField('rarity', validators=[DataRequired()], coerce=int)
        target = SelectField('target', validators=[DataRequired()], coerce=int)
        pro_con = StringField('pro_con', validators=[DataRequired()])
        trophies = SelectField('trophies', validators=[DataRequired()], coerce=int)
        evolution = SelectField('evolution', validators=[DataRequired()], coerce=int)
        speed = TextAreaField('speed', validators=[DataRequired()])
        spawn_time = TextAreaField('spawn_time', validators=[DataRequired()])
        elixir = TextAreaField('elixir', validators=[DataRequired()])
        description = TextAreaField('description', validators=[DataRequired()])
        image = TextAreaField('image', validators=[DataRequired()])
