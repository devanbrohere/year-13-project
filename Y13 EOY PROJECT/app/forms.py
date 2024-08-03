from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField, SelectMultipleField, FileField, SubmitField, PasswordField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, NumberRange
from wtforms.validators import DataRequired, Optional, ValidationError, Email, EqualTo
import app.models
from app.models import Rarity, Targets, Trophies, Evolution, Special
from wtforms.validators import DataRequired, Email, EqualTo

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class Add_Card(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rarity = SelectField('Rarity', coerce=int, validators=[DataRequired()])
    target = SelectField('Target', coerce=int, validators=[DataRequired()])
    trophies = SelectField('Trophies', coerce=int, validators=[DataRequired()])
    evolution = SelectField('Evolution', coerce=int, validators=[DataRequired()])
    special = SelectField('Special', coerce=int, validators=[DataRequired()])
    speed = TextAreaField('Speed', validators=[DataRequired()])
    spawn_time = TextAreaField('Spawn Time', validators=[DataRequired()])
    elixir = IntegerField('Elixir', validators=[DataRequired(), NumberRange(min=0, max=9)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])
    

    def __init__(self, *args, **kwargs):
        super(Add_Card, self).__init__(*args, **kwargs)
        # rarities = models.Rarity.query.all()
        self.rarity.choices = [(rarity.id, rarity.type) for rarity in Rarity.query.all()]
        self.target.choices = [(target.id, target.type) for target in Targets.query.all()]
        self.trophies.choices = [(trophy.id, trophy.trophies) for trophy in Trophies.query.all()]
        self.special.choices = [(special.id, special.name) for special in Special.query.all()]
        self.evolution.choices = [(evolution.id, evolution.cycles) for evolution in Evolution.query.all()]


class Add_Rarity(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])


class Add_Target(FlaskForm):
    type = StringField('type', validators=[DataRequired()])


class Add_Trophies(FlaskForm):
    trophies = IntegerField('trophies', validators=[DataRequired(), NumberRange(min=0)])
    arena = StringField('arena', validators=[DataRequired()])


class Add_Evolution(FlaskForm):
    cycles = IntegerField('Cycles', validators=[DataRequired(), NumberRange(min=0)])
    stat_boost = StringField('Stat Boost', validators=[DataRequired()])
    special_ability = StringField('Ablity', validators=[DataRequired()])


class Add_Special(FlaskForm):
    name = StringField('special name', validators=[DataRequired()])
    activation_elexir = IntegerField('Activation elexir', validators=[DataRequired(), NumberRange(min=0)])
    description = StringField('description', validators=[DataRequired()])


class add_type(FlaskForm):
    add_type = SelectField('Add Type', validators=[DataRequired()], coerce=int)


