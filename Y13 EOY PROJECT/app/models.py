from app.routes import db  # Import the SQLAlchemy database instance
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing utilities

# Association table for many-to-many relationship between Cards and Targets
Card_targets = db.Table('card_targets',
                        db.Column('card_id', db.Integer, db.ForeignKey('Card.id'), primary_key=True),
                        db.Column('target_id', db.Integer, db.ForeignKey('Targets.id'), primary_key=True))


class Cards(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())  # Name of the card
    description = db.Column(db.Text())  # Description of the card
    rarity = db.Column(db.Integer, db.ForeignKey("Rarity.id"))  # Foreign key to Rarity
    rarity_type = db.relationship("Rarity", backref="Rarity")  # Relationship to Rarity model
    Min_trophies_unlocked = db.Column(db.Integer, db.ForeignKey("Min_trophies_unlocked.id"))  # Foreign key to Trophies
    trophies = db.relationship("Trophies", backref="Trophies")  # Relationship to Trophies model
    evolution = db.Column(db.Integer, db.ForeignKey("Evolution.id"))  # Foreign key to Evolution
    evo = db.relationship("Evolution", backref="Evolution")  # Relationship to Evolution model
    Special = db.Column(db.Integer, db.ForeignKey("Special.id"))  # Foreign key to Special
    special = db.relationship("Special", backref="Special")  # Relationship to Special model
    card_type = db.Column(db.Integer, db.ForeignKey("Card_type.id"))
    card = db.relationship("Card_type", backref="Card_type")
    speed = db.Column(db.Text())  # Speed attribute of the card
    elixir = db.Column(db.Text())  # Elixir cost of the card
    pending = db.Column(db.Integer, default=0)
    image = db.Column(db.Text())  # Image URL or path of the card
    card_target = db.relationship('Targets', secondary=Card_targets, backref=db.backref
                                  ('Card', lazy='dynamic'))  # Many-to-many relationship with Targets


# Special model representing special abilities or characteristics of a card
class Special(db.Model):
    __tablename__ = "Special"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())  # Name of the special ability
    activation_elixir = db.Column(db.Text())  # Elixir cost to activate the special ability
    description = db.Column(db.Text())  # Description of the special ability


# Rarity model representing the rarity level of a card
class Rarity(db.Model):
    __tablename__ = "Rarity"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)


class Card_type(db.Model):
    __tablename__ = "Card_type"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text())
    description = db.Column(db.Text())


# Evolution model representing the evolution stages of a card
class Evolution(db.Model):
    __tablename__ = "Evolution"
    id = db.Column(db.Integer, primary_key=True)
    cycles = db.Column(db.Text())
    special_ability = db.Column(db.Text())
    cycle_for = db.Column(db.Text(), nullable=False)
    stat_boost = db.Column(db.String(50), nullable=False)
    image_evo = db.Column(db.Text())


# Targets model representing the potential targets for a card
class Targets(db.Model):
    __tablename__ = "Targets"
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Text())  # Name or type of target
    description = db.Column(db.Text())  # Description of the target


# Trophies model representing the minimum trophies required to unlock a card
class Trophies(db.Model):
    __tablename__ = "Min_trophies_unlocked"
    id = db.Column(db.Integer, primary_key=True)
    trophies = db.Column(db.Text())  # Minimum number of trophies required
    arena = db.Column(db.Text())  # Arena associated with the trophies
    image = db.Column(db.Text())


class Card_stats(db.Model):
    __tablename__ = 'Card_stats'
    id = db.Column(db.Integer, primary_key=True)  # Primary key for Card_stats
    card_id = db.Column(db.Integer, db.ForeignKey("Card.id"))  # Foreign key to Cards
    card = db.relationship("Cards", backref=db.backref("card_stats", lazy=True))  # Relationship to Cards
    level = db.Column(db.Text())
    health = db.Column(db.Text())
    damage = db.Column(db.Text())
    damage_per_sec = db.Column(db.Text())


# User model representing a user in the system
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)  # Full name of the user
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email, must be unique
    password_hash = db.Column(db.String(128), nullable=False)  # Hashed password for security

    # deck = db.relationship("Deck", backref="user")
    # Method to set the` user's password (hashes the password)
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    # Method to check if the provided password matches the stored hashed password
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Deck(db.Model):
    __tablename__ = 'Deck'
    id = db.Column(db.Integer, primary_key=True)

    card1_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card1 = db.relationship("Cards", foreign_keys=[card1_id], backref="card1_deck")

    card2_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card2 = db.relationship("Cards", foreign_keys=[card2_id], backref="card2_deck")

    card3_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card3 = db.relationship("Cards", foreign_keys=[card3_id], backref="card3_deck")

    card4_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card4 = db.relationship("Cards", foreign_keys=[card4_id], backref="card4_deck")

    card5_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card5 = db.relationship("Cards", foreign_keys=[card5_id], backref="card5_deck")

    card6_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card6 = db.relationship("Cards", foreign_keys=[card6_id], backref="card6_deck")

    card7_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card7 = db.relationship("Cards", foreign_keys=[card7_id], backref="card7_deck")

    card8_id = db.Column(db.Integer, db.ForeignKey("Card.id"))
    card8 = db.relationship("Cards", foreign_keys=[card8_id], backref="card8_deck")

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    user = db.relationship("User", backref="decks", primaryjoin="User.id == Deck.user_id")

    # Method to return a sorted list of card IDs for comparison
    def sorted_card_ids(self):
        return sorted([
            self.card1_id, self.card2_id, self.card3_id, self.card4_id,
            self.card5_id, self.card6_id, self.card7_id, self.card8_id
        ])
