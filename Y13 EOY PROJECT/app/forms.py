from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms import SelectMultipleField, FileField, EmailField, SubmitField, PasswordField, validators
from wtforms.validators import DataRequired, NumberRange, Length
from wtforms.validators import ValidationError, Email, EqualTo
from app.models import Rarity, Targets, Trophies, Evolution, Special, Cards, Card_type


class New_user(FlaskForm):
    full_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class Add_Card(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rarity = SelectField('Rarity', coerce=int, validators=[DataRequired()])
    target = SelectMultipleField('Target', coerce=int, validators=[DataRequired()])  # Changed to SelectMultipleField
    trophies = SelectField('Trophies', coerce=int, validators=[DataRequired()])
    evolution = SelectField('Evolution', coerce=int, validators=[DataRequired()])
    card_type = SelectField('Card type', coerce=int, validators=[DataRequired()])
    special = SelectField('Special', coerce=int, validators=[DataRequired()])
    speed = TextAreaField('Speed', validators=[DataRequired()])
    spawn_time = TextAreaField('Spawn Time', validators=[DataRequired()])
    elixir = IntegerField('Elixir', validators=[DataRequired(), NumberRange(min=1, max=9)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(Add_Card, self).__init__(*args, **kwargs)
        self.rarity.choices = [(rarity.id, rarity.type) for rarity in Rarity.query.all()]
        self.target.choices = [(target.id, target.target) for target in Targets.query.all()]  # Choices for multiple targets
        self.trophies.choices = [(trophy.id, trophy.trophies) for trophy in Trophies.query.all()]
        self.special.choices = [(special.id, special.name) for special in Special.query.all()]
        self.card_type.choices = [(card_type.id, card_type.type) for card_type in Card_type.query.all()]
        self.evolution.choices = [(evolution.id, evolution.cycle_for) for evolution in Evolution.query.all()]


class Add_Rarity(FlaskForm):
    type = StringField('Type', validators=[DataRequired()])


class Add_Target(FlaskForm):
    target = StringField('type', validators=[DataRequired()])
    description = StringField('type', validators=[DataRequired()])


class Add_Trophies(FlaskForm):
    trophies = IntegerField('trophies', validators=[DataRequired(), NumberRange(min=0)])
    arena = StringField('arena', validators=[DataRequired()])


class Add_Evolution(FlaskForm):
    cycles = IntegerField('Cycles', validators=[DataRequired(), NumberRange(min=1, max=2)])
    stat_boost = StringField('Stat Boost', validators=[DataRequired()])
    special_ability = StringField('Ability', validators=[DataRequired()])
    cycle_for = SelectField('Cycles For', coerce=int, validators=[DataRequired()])
    image_evo = FileField('Image', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(Add_Evolution, self).__init__(*args, **kwargs)
        # Assuming Cards has a 'name' attribute to display in the dropdown
        self.cycle_for.choices = [(card.id, card.name) for card in Cards.query.all()]


class Add_Special(FlaskForm):
    name = StringField('special name', validators=[DataRequired()])
    activation_elexir = IntegerField('Activation elexir', validators=[DataRequired(), NumberRange(min=0)])
    description = StringField('description', validators=[DataRequired()])

class Add_card_stats(FlaskForm):
    card_id = SelectField('Card', coerce=int, validators=[DataRequired()])
    health = IntegerField('Health', validators=[DataRequired(), NumberRange(min=0)])
    level = IntegerField('Level', validators=[DataRequired(), NumberRange(min=1, max=15)])
    damage = IntegerField('Damage', validators=[DataRequired(), NumberRange(min=1)])
    damage_sec = IntegerField('Damage Sec', validators=[DataRequired(), NumberRange(min=0)])
