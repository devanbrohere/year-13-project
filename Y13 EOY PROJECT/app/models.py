from app.routes import db
from flask_login import UserMixin


class Cards(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    rarity = db.Column(db.Integer, db.ForeignKey("Rarity.id"))
    rarity_type = db.relationship("Rarity", backref="Rarity")
    targets = db.Column(db.Integer, db.ForeignKey("Targets.id"))
    target = db.relationship("Targets", backref="Targets")
    Min_trophies_unlocked = db.Column(db.Integer, db.ForeignKey("Min_trophies_unlocked.id"))
    Trophies = db.relationship("Trophies", backref="Trophies")
    evolution = db.Column(db.Integer, db.ForeignKey("Evolution.id"))
    evo = db.relationship("Evolution", backref="Evolution")
    speed = db.Column(db.Text())
    spawn_time = db.Column(db.Text())
    elixir = db.Column(db.Text())
    image = db.Column(db.Text())


class Rarity(db.Model):
    __tablename__ = "Rarity"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())


class Evolution(db.Model):
    __tablename__ = "Evolution"
    id = db.Column(db.Integer, primary_key=True)
    cycles = db.Column(db.String(50), nullable=False)
    stat_boost = db.Column(db.String(50), nullable=False)
    special_ability = db.Column(db.String(50), nullable=False)


class Targets(db.Model):
    __tablename__ = "Targets"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())


class Trophies(db.Model):
    __tablename__ = "Min_trophies_unlocked"
    id = db.Column(db.Integer, primary_key=True)
    trophies = db.Column(db.Text())
    arena = db.Column(db.Text())


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
