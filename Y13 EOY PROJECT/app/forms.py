from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField
from wtforms import SelectMultipleField, FileField, SubmitField, PasswordField, validators,  HiddenField
from wtforms.validators import DataRequired, NumberRange, Length
from wtforms.validators import Email, EqualTo
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
    trophies = SelectField('Trophies', coerce=int, validators=[DataRequired()], render_kw={"class": ""})
    evolution = SelectField('Evolution', coerce=int, validators=[])
    card_type = SelectField('Card type', coerce=int, validators=[DataRequired()])
    special = SelectField('Special', coerce=int, validators=[DataRequired()])
    speed = TextAreaField('Speed', validators=[DataRequired()])
    elixir = IntegerField('Elixir', validators=[DataRequired(), NumberRange(min=1, max=9)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(Add_Card, self).__init__(*args, **kwargs)
        self.rarity.choices = [(rarity.id, rarity.type) for rarity in Rarity.query.all()]
        self.target.choices = [(target.id, target.target) for target in Targets.query.all()]  # Choices for multiple targets
        self.trophies.choices = [(trophy.id, trophy.arena) for trophy in Trophies.query.all()]
        self.special.choices = [(special.id, special.name) for special in Special.query.all()]
        self.card_type.choices = [(card_type.id, card_type.type) for card_type in Card_type.query.all()]
        self.evolution.choices = [(0, 'None')] + [(evolution.id, evolution.cycle_for) for evolution in Evolution.query.all()]


class Add_Evolution(FlaskForm):
    cycles = IntegerField('Cycles', validators=[DataRequired(), NumberRange(min=1, max=2)])
    stat_boost = StringField('Stat Boost', validators=[DataRequired()])
    special_ability = StringField('Ability', validators=[DataRequired()])
    cycle_for = TextAreaField('Cycles For', validators=[DataRequired()])
    image_evo = FileField('Image', validators=[DataRequired()])



class Add_Special(FlaskForm):
    name = StringField('special name', validators=[DataRequired()])
    activation_elexir = IntegerField('Activation elexir', validators=[DataRequired(), NumberRange(min=0)])
    description = StringField('description', validators=[DataRequired()])


class Add_card_stats(FlaskForm):
    health = IntegerField('Minimum Health', validators=[DataRequired(), NumberRange(min=10)])
    damage = IntegerField('Minimum Damage', validators=[DataRequired(), NumberRange(min=0)])
    damage_sec = IntegerField('Minimum Damage per Second', validators=[DataRequired(), NumberRange(min=0)])


class PendingApprovalForm(FlaskForm):
    card_id = HiddenField("Card ID")
    approve = SubmitField("Approve")
    reject = SubmitField("Reject")

