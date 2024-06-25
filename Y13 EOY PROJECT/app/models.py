from app.routes import db

class Cards(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    rarity = db.Column(db.Integer, db.ForeignKey("Rarity.id"))
    rarity_type = db.relationship("Rarity", backref="Rarity")
    Attack_type = db.Column(db.Integer, db.ForeignKey("Attack_type.id"))
    attack = db.relationship("AttackType", backref="AttackType")
    Min_trophies_unlocked = db.Column(db.Integer, db.ForeignKey("Min_trophies_unlocked.id"))
    Trophies = db.relationship("Trophies", backref="Trophies")
    evolution = db.Column(db.Integer, db.ForeignKey("Evolution.id"))
    evo = db.relationship("Evolution", backref="Evolution")


class Rarity(db.Model):
    __tablename__ = "Rarity"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())


class Evolution(db.Model):
    __tablename__ = "Evolution"
    id = db.Column(db.Integer, primary_key=True)
    cycles = db.Column(db.Text())
    stat_boost = db.Column(db.Text())
    special_ablity = db.Column(db.Text())


class AttackType(db.Model):
    __tablename__ = "Attack_type"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())
    description = db.Column(db.Text())


class Trophies(db.Model):
    __tablename__ = "Min_trophies_unlocked"
    id = db.Column(db.Integer, primary_key=True)
    trophies = db.Column(db.Text())
    arena = db.Column(db.Text())
