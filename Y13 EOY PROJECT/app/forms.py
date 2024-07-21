from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class Add_Card(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rarity = SelectField('Rarity', validators=[DataRequired()], coerce=int)
    target = SelectField('Target', validators=[DataRequired()], coerce=int)
    pro_con = StringField('Pro/Con', validators=[DataRequired()])
    trophies = SelectField('Trophies', validators=[DataRequired()], coerce=int)
    evolution = SelectField('Evolution', validators=[DataRequired()], coerce=int)
    speed = TextAreaField('Speed', validators=[DataRequired()])
    spawn_time = TextAreaField('Spawn Time', validators=[DataRequired()])
    elixir = TextAreaField('Elixir', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = TextAreaField('Image', validators=[DataRequired()])

    def __init__(self, rarity_choices, target_choices, trophy_choices, evolution_choices, *args, **kwargs):
        super(Add_Card, self).__init__(*args, **kwargs)
        self.rarity.choices = rarity_choices
        self.target.choices = target_choices
        self.trophies.choices = trophy_choices
        self.evolution.choices = evolution_choices
