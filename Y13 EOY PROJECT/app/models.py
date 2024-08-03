from app.routes import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

Card_stats = db.Table('card_stats',
    db.Column('card_id', db.Integer, db.ForeignKey('Card.id'), primary_key=True),
    db.Column('health_id', db.Integer, db.ForeignKey('Health.id'), primary_key=True),
    db.Column('level_id', db.Integer, db.ForeignKey('Level.id'), primary_key=True),
    db.Column('damage', db.Integer, db.ForeignKey('Damage.id'), primary_key=True),
    db.Column('damage_per_sec_id', db.Integer, db.ForeignKey('Damage_per_sec.id'), primary_key=True),
)
Card_targets = db.Table('card_targets',
    db.Column('card_id', db.Integer, db.ForeignKey('Card.id'), primary_key=True),
    db.Column('target_id', db.Integer, db.ForeignKey('Targets.id'), primary_key=True))


class Cards(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    rarity = db.Column(db.Integer, db.ForeignKey("Rarity.id"))
    rarity_type = db.relationship("Rarity", backref="Rarity")
    Min_trophies_unlocked = db.Column(db.Integer, db.ForeignKey("Min_trophies_unlocked.id"))
    Trophies = db.relationship("Trophies", backref="Trophies")
    evolution = db.Column(db.Integer, db.ForeignKey("Evolution.id"))
    evo = db.relationship("Evolution", backref="Evolution")
    Special = db.Column(db.Integer, db.ForeignKey("Special.id"))
    special = db.relationship("Special", backref="Special")
    speed = db.Column(db.Text())
    spawn_time = db.Column(db.Text())
    elixir = db.Column(db.Text())
    image = db.Column(db.Text())
    card_health = db.relationship('Health', secondary=Card_stats, backref=db.backref
                                  ('Card', lazy='dynamic'))
    card_level = db.relationship('Level', secondary=Card_stats, backref=db.backref
                                  ('Card', lazy='dynamic'))
    card_damage = db.relationship('Damage', secondary=Card_stats, backref=db.backref
                                  ('Card', lazy='dynamic'))
    card_damage_per_sec = db.relationship('Damage_per_sec', secondary=Card_stats, backref=db.backref
                                  ('Card', lazy='dynamic'))
    card_target = db.relationship('Targets', secondary=Card_targets, backref=db.backref
                                  ('Card', lazy='dynamic'))

class Damage_per_sec(db.Model):
    __tablename__ = 'Damage_per_sec'
    id = db.Column(db.Integer, primary_key=True)
    damage_per_sec = db.Column(db.Text())

class Damage(db.Model):
    __tablename__ = 'Damage'
    id = db.Column(db.Integer, primary_key=True)
    damage = db.Column(db.Text())

class Health(db.Model):
    __tablename__ = 'Health'
    id = db.Column(db.Integer, primary_key=True)
    health = db.Column(db.Text())

class Level(db.Model):
    __tablename__ = 'Level'
    id = db.Column(db.Integer, primary_key=True)

class Special(db.Model):
    __tablename__ = "Special"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    activation_elixir = db.Column(db.Text())
    description = db.Column(db.Text())


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



class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
