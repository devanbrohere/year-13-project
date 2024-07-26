from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Optional
import app.models
from app.models import Rarity, Targets, Trophies, Evolution, Special


class Add_Card(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rarity = SelectField('Rarity', validators=[DataRequired()], coerce=int)
    target = SelectField('Target', validators=[DataRequired()], coerce=int)
    trophies = SelectField('Trophies', validators=[DataRequired()], coerce=int)
    evolution = SelectField('Evolution', validators=[DataRequired()], coerce=int)
    speed = TextAreaField('Speed', validators=[DataRequired()])
    spawn_time = TextAreaField('Spawn Time', validators=[DataRequired()])
    elixir = TextAreaField('Elixir', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'], 'Images Only!')])
    special = TextAreaField('Special', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(Add_Card, self).__init__(*args, **kwargs)
        # rarities = models.Rarity.query.all()
        self.rarity.choices = [(rarity.id, rarity.type) for rarity in Rarity.query.all()]
        self.target.choices = [(target.id, target.type) for target in Targets.query.all()]
        self.trophies.choices = [(trophy.id, trophy.trophies) for trophy in Trophies.query.all()]
        self.special.choices = [(special.id, special.special) for special in Special.query.all()]
        self.evolution.choices = [(evolution.id, evolution.cycles) for evolution in Evolution.query.all()]

