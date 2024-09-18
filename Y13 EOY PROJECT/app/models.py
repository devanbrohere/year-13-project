from werkzeug.security import generate_password_hash, check_password_hash
from app.routes import db

Card_targets = db.Table('card_targets',
                        db.Column('card_id', db.Integer,
                                  db.ForeignKey('Card.id'), primary_key=True),
                        db.Column('target_id', db.Integer,
                                  db.ForeignKey('Targets.id'),
                                  primary_key=True))


class Cards(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    rarity = db.Column(db.Integer, db.ForeignKey("Rarity.id"))
    rarity_type = db.relationship("Rarity", backref="Rarity")
    Min_trophies_unlocked = \
        db.Column(db.Integer, db.ForeignKey("Min_trophies_unlocked.id"))
    trophies = db.relationship("Trophies", backref="Trophies")
    evolution = db.Column(db.Integer, db.ForeignKey("Evolution.id"))
    evo = db.relationship("Evolution", backref="Evolution")
    Special = db.Column(db.Integer, db.ForeignKey("Special.id"))
    special = db.relationship("Special", backref="Special")
    card_type = db.Column(db.Integer, db.ForeignKey("Card_type.id"))
    card = db.relationship("Card_type", backref="Card_type")
    speed = db.Column(db.Text())
    elixir = db.Column(db.Text())
    pending = db.Column(db.Integer, default=0)
    image = db.Column(db.Text())
    card_target = db.relationship('Targets', secondary=Card_targets,
                                  backref=db.backref
                                  ('Card', lazy='dynamic'))


class Special(db.Model):
    __tablename__ = "Special"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    activation_elixir = db.Column(db.Text())
    description = db.Column(db.Text())


class Rarity(db.Model):
    __tablename__ = "Rarity"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)


class Card_type(db.Model):
    __tablename__ = "Card_type"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())
    description = db.Column(db.Text())


class Evolution(db.Model):
    __tablename__ = "Evolution"
    id = db.Column(db.Integer, primary_key=True)
    cycles = db.Column(db.Text())
    special_ability = db.Column(db.Text())
    cycle_for = db.Column(db.Text(), nullable=False)
    stat_boost = db.Column(db.String(50), nullable=False)
    image_evo = db.Column(db.Text())


class Targets(db.Model):
    __tablename__ = "Targets"
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Text())
    description = db.Column(db.Text())


class Trophies(db.Model):
    __tablename__ = "Min_trophies_unlocked"
    id = db.Column(db.Integer, primary_key=True)
    trophies = db.Column(db.Text())
    arena = db.Column(db.Text())
    image = db.Column(db.Text())


class Card_stats(db.Model):
    __tablename__ = 'Card_stats'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card = db.relationship("Cards",
                           backref=db.backref("card_stats", lazy=True))
    level = db.Column(db.Text())
    health = db.Column(db.Text())
    damage = db.Column(db.Text())
    damage_per_sec = db.Column(db.Text())


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Deck(db.Model):
    __tablename__ = 'Deck'
    id = db.Column(db.Integer, primary_key=True)

    card1_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card1 = db.relationship("Cards",
                            foreign_keys=[card1_id], backref="card1_deck")

    card2_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card2 = db.relationship("Cards",
                            foreign_keys=[card2_id], backref="card2_deck")

    card3_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card3 = db.relationship("Cards",
                            foreign_keys=[card3_id], backref="card3_deck")

    card4_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card4 = db.relationship("Cards",
                            foreign_keys=[card4_id], backref="card4_deck")

    card5_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card5 = db.relationship("Cards",
                            foreign_keys=[card5_id], backref="card5_deck")

    card6_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card6 = db.relationship("Cards",
                            foreign_keys=[card6_id], backref="card6_deck")

    card7_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card7 = db.relationship("Cards",
                            foreign_keys=[card7_id], backref="card7_deck")

    card8_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card8 = db.relationship("Cards",
                            foreign_keys=[card8_id], backref="card8_deck")

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    user = db.relationship("User",
                           backref="decks",
                           primaryjoin="User.id == Deck.user_id")

    def sorted_card_ids(self):
        return sorted([
            self.card1_id, self.card2_id, self.card3_id, self.card4_id,
            self.card5_id, self.card6_id, self.card7_id, self.card8_id
        ])
