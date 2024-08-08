from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms import SelectMultipleField, FileField, EmailField, SubmitField, PasswordField, validators
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, NumberRange, Length
from wtforms.validators import Optional, ValidationError, Email, EqualTo
import app.models
from app.models import Rarity, Targets, Trophies, Evolution, Special
from wtforms.validators import DataRequired, Email, EqualTo

class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[Email(message='Please enter a valid email.')])
    password = PasswordField('Password', [
        DataRequired(message='Password is required.'),
        EqualTo('confirm', message='Passwords must match.'),
        Length(min=6, max=10, message='Password must be between 6 and 10 characters long.')
    ])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Password confirmation is required.')
    ])
    name = StringField('Name', validators=[
        DataRequired(message='Name is required.'),
        Length(min=6, max=12, message='Name must be between 6 and 12 characters long.')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[Email(message='Please enter a valid email.')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, max=10, message='Password must be between 6 and 10 characters long.')
    ])
    submit = SubmitField('Login')



class Add_Card(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rarity = SelectField('Rarity', coerce=int, validators=[DataRequired()])
    target = SelectMultipleField('Target', coerce=int, validators=[DataRequired()])  # Changed to SelectMultipleField
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
        self.rarity.choices = [(rarity.id, rarity.type) for rarity in Rarity.query.all()]
        self.target.choices = [(target.id, target.type) for target in Targets.query.all()]  # Choices for multiple targets
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


