from app import app
from sqlalchemy.exc import IntegrityError
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "clash.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images')
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'
db = SQLAlchemy(app)


import app.models as models
from app.models import Cards, User, Rarity, Targets, Card_type, Deck
from app.forms import Add_Card, New_user, LoginForm, Add_Evolution
from app.forms import Add_Special, Add_card_stats, AddDeckForm


def get_starting_level(rarity):
    if rarity == 1:  # Legendary
        return 9
    elif rarity == 2:  # Epic
        return 6
    elif rarity == 3:  # Rare
        return 3
    elif rarity == 4:  # Common
        return 1
    elif rarity == 5:  # Champion
        return 9


def calculate_levels(starting_level, health, damage, damage_per_sec):
    levels = []
    level_count = 15  # Maximum level
    for level in range(starting_level, level_count + 1):
        multiplier = 1.1 ** (level - starting_level)  # Increase by 10% per level
        levels.append({
            'level': level,
            'health': round(health * multiplier),
            'damage': round(damage * multiplier),
            'damage_per_sec': round(damage_per_sec * multiplier),
        })
    return levels


@app.errorhandler(404)
def page_not_found(e):
    # Render a custom 404 error page
    return render_template('404.html', pagename="error"), 404


@app.route("/")
def home():
    # Render the home page
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/card/<int:id>')
def card(id):
    try:
        card = models.Cards.query.filter_by(id=id, pending=1).first_or_404()  # Ensure the card has permission 1

        card_stats = models.Card_stats.query.filter_by(card_id=id).all()

        # Debug output to ensure stats are fetched
        print("Card:", card)
        print("Card Stats:", card_stats)

        return render_template('card.html', card=card, card_stats=card_stats)
    except OverflowError:
        flash("no card avaiable")
        return redirect(url_for("cards"))


@app.route('/cards')
def cards():
    rarity_id = request.args.get('Rarity')
    target_id = request.args.get('Target')
    card_type_id = request.args.get('CardType')
    elixir_cost = request.args.get('Elixir')

    query = Cards.query.filter_by(pending=1)  # Only select cards with permission = 1

    if rarity_id and rarity_id != 'all':
        query = query.filter(Cards.rarity == int(rarity_id))

    if target_id and target_id != 'all':
        query = query.filter(Cards.card_target.any(id=int(target_id)))

    if card_type_id and card_type_id != 'all':
        query = query.filter(Cards.card_type == int(card_type_id))

    if elixir_cost and elixir_cost != 'all':
        query = query.filter(Cards.elixir == int(elixir_cost))

    cards = query.all()
    rarity = Rarity.query.order_by(Rarity.type).all()
    attack_type = Targets.query.order_by(Targets.target).all()
    card_types = Card_type.query.order_by(Card_type.type).all()
    elixir_costs = sorted({card.elixir for card in Cards.query.all()})  # Get distinct elixir values

    if not cards:
        flash('No cards available in the database', 'danger')
        return redirect(url_for('cards'))

    return render_template('cards.html', cards=cards, rarity=rarity,
                           attack_type=attack_type, card_types=card_types,
                           elixir_costs=elixir_costs)


@app.route('/deck')
def deck():
    user_id = request.args.get('User')  # Get the 'User' query parameter

    # Base query for decks
    query = Deck.query.join(User)

    # Filter by user if provided
    if user_id and user_id != 'all':
        query = query.filter(Deck.user_id == int(user_id))

    # Execute the query to fetch decks
    decks = query.all()

    deck_data = []

    for deck in decks:
        # Extract card attributes from the deck
        cards = [
            deck.card1, deck.card2, deck.card3, deck.card4,
            deck.card5, deck.card6, deck.card7, deck.card8
        ]
        # Calculate average elixir cost
        total_elixir = 0
        count = 0
        for card in cards:
            if card and card.elixir:
                try:
                    elixir_cost = float(card.elixir)
                    total_elixir += elixir_cost
                    count += 1
                except ValueError:
                    pass
        average_elixir = total_elixir / count if count > 0 else 0

        # Store the deck and its related data, including the user
        deck_data.append({
            'cards': cards,
            'average_elixir': average_elixir,
            'user': deck.user  # Assuming a relationship deck.user exists
        })

    # Fetch all users for the dropdown
    users = User.query.order_by(User.full_name).all()

    return render_template('deck.html', deck_data=deck_data,
                           users=users, selected_user=user_id)


@app.route("/admin")
def admin():
    if 'user_id' not in session or session.get('user_id') != 7:
        flash("Admin access only", 'error')
        return redirect(url_for('home'))
    else:
        pending_cards = models.Cards.query.filter_by(pending=0).all()
        return render_template("admin.html", pending_cards=pending_cards)


@app.route("/admin/approve_card/<int:id>")
def approve(id):
    if 'user_id' not in session or session.get('user_id') != 7:
        flash("Admin access only", 'error')
        return redirect(url_for('home'))
    else:
        pending_card = models.Cards.query.get_or_404(id)
        # Approve the card
        pending_card.pending = 1
        db.session.add(pending_card)
        db.session.commit()
        flash("Card and its Evolution (if any) have been approved", "success")
        return redirect(url_for("admin"))


@app.route("/admin/reject_card/<int:id>")
def reject(id):
    if 'user_id' not in session or session.get('user_id') != 7:
        flash("Admin access only", 'error')
        return redirect(url_for('home'))

    # Fetch the card to delete
    card_to_delete = models.Cards.query.get_or_404(id)

    # Check if the card has an associated evolution
    if card_to_delete.evolution:
        # Fetch the evolution to delete
        evolution_to_delete = models.Evolution.query.get(card_to_delete.evolution)
        if evolution_to_delete:
            db.session.delete(evolution_to_delete)

    if card_to_delete.special:
        # Ensure card_to_delete.special is an integer ID
        special_id = card_to_delete.special if isinstance(card_to_delete.special, int) else card_to_delete.special.id
        special_to_delete = models.Special.query.get(special_id)
        if special_to_delete:
            db.session.delete(special_to_delete)

    # Delete the card
    db.session.delete(card_to_delete)
    db.session.commit()

    flash("Card and its Evolution (if any) have been deleted", "success")
    return redirect(url_for("admin"))


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("login"))

    form = Add_Card()
    evolution_form = Add_Evolution()
    card_stats_form = Add_card_stats()
    special_form = Add_Special()

    if form.validate_on_submit() and card_stats_form.validate_on_submit() and 'submit_card_and_stats' in request.form:
        new_card = models.Cards()
        new_card.name = form.name.data.capitalize()
        new_card.description = form.description.data
        new_card.rarity = form.rarity.data
        new_card.Min_trophies_unlocked = form.trophies.data
        new_card.speed = form.speed.data
        new_card.card_type = form.card_type.data
        new_card.elixir = form.elixir.data

        if form.special.data != 0:  # Check if "None" was selected
            new_card.Special = form.special.data
        else:
            new_card.Special = None

        if form.evolution.data != 0:  # Check if "None" was selected
            new_card.evolution = form.evolution.data
        else:
            new_card.evolution = None

        # Handle many-to-many relationship for card_target
        target_ids = form.target.data
        targets = models.Targets.query.filter(models.Targets.id.in_(target_ids)).all()
        new_card.card_target = targets

        # Handle file upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            form.image.data.save(file_path)
            new_card.image = f'images/{filename}'
        else:
            new_card.image = None

        try:
            db.session.add(new_card)
            db.session.commit()

            # Process Card Stats
            starting_level = get_starting_level(new_card.rarity)
            levels = calculate_levels(starting_level,
                                      card_stats_form.health.data,
                                      card_stats_form.damage.data,
                                      card_stats_form.damage_sec.data)

            for level_data in levels:
                card_stat = models.Card_stats()
                card_stat.card_id = new_card.id
                card_stat.level = level_data['level']
                card_stat.health = level_data['health']
                card_stat.damage = level_data['damage']
                card_stat.damage_per_sec = level_data['damage_per_sec']
                db.session.add(card_stat)
            db.session.commit()
            flash("Waiting for admin to accept")

            if 'user_id' not in session or session.get('user_id') != 7:
                flash("Admin access only", 'error')
                return redirect(url_for('home'))
            else:
                return redirect(url_for('admin'))

        except IntegrityError:
            db.session.rollback()
            flash('Card with this name already exists. Please choose a different name.', 'danger')

    return render_template('add_card.html', form=form, evolution_form=evolution_form,
                           card_stats_form=card_stats_form, special_form=special_form,
                           title="Add Card")


@app.route('/add_special', methods=['GET', 'POST'])
def add_special():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("login"))
    evolution_form = Add_Evolution()
    form = Add_Card()
    special_form = Add_Special()

    if 'submit_special' in request.form and special_form.validate_on_submit():
        new_special = models.Special()
        new_special.name = special_form.name.data
        new_special.activation_elixir = special_form.elixir.data
        new_special.description = special_form.description.data
        try:
            db.session.add(new_special)
            db.session.commit()
            flash("Special ablity added")
        except IntegrityError:
            db.session.rollback()
            flash("Special ability already in the database")
    return render_template("add_card.html", form=form, evolution_form=evolution_form,
                           special_form=special_form,
                           title="Add Special")


@app.route("/add_evolution", methods=['GET', 'POST'])
def add_evolution():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("login"))

    evolution_form = Add_Evolution()
    form = Add_Card()
    special_form = Add_Special()

    if 'submit_evolution' in request.form and evolution_form.validate_on_submit():
        new_evolution = models.Evolution()
        new_evolution.cycle_for = evolution_form.cycle_for.data
        new_evolution.cycles = evolution_form.cycles.data
        new_evolution.stat_boost = evolution_form.stat_boost.data
        new_evolution.special_ability = evolution_form.special_ability.data

        # Handle file upload for evolution
        if evolution_form.image_evo.data:
            filename = secure_filename(evolution_form.image_evo.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            evolution_form.image_evo.data.save(file_path)
            new_evolution.image_evo = f'images/{filename}'
        else:
            new_evolution.image_evo = None

        try:
            db.session.add(new_evolution)
            db.session.commit()
            flash("Evolution added")
        except IntegrityError:
            db.session.rollback()
            flash('Evolution with this type already exists. Please choose a different type.', 'danger')

    return render_template('add_card.html', evolution_form=evolution_form,
                           special_form=special_form, form=form, title="Add Evolution")


@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You need to be logged in to add a deck.", "danger")
        return redirect(url_for('login'))

    # Handle POST request for form submission
    if request.method == 'POST':
        deck_cards = []
        for i in range(1, 9):  # 8 card slots
            card_id = request.form.get(f'card{i}_id')
            if card_id:
                card = Cards.query.get(card_id)
                if card:
                    deck_cards.append(card)

        # Ensure at least 8 cards are selected
        if len(deck_cards) < 8:
            flash("You must select 8 cards for the deck.", "danger")
            return redirect(url_for('add_deck'))

        # Check if the first card has an evolution and use its image
        card1 = deck_cards[0] if len(deck_cards) > 0 else None
        if card1 and card1.evolution:
            evolution_image = card1.evo.image_evo
            flash(f"Using evolution image: {evolution_image}", "info")
            # You can now use `evolution_image` in your template or store it

        # Add the new deck to the database
        new_deck = models.Deck()
        new_deck.user_id = session['user_id']
        new_deck.card1_id = deck_cards[0].id
        new_deck.card2_id = deck_cards[1].id
        new_deck.card3_id = deck_cards[2].id
        new_deck.card4_id = deck_cards[3].id
        new_deck.card5_id = deck_cards[4].id
        new_deck.card6_id = deck_cards[5].id
        new_deck.card7_id = deck_cards[6].id
        new_deck.card8_id = deck_cards[7].id
        db.session.add(new_deck)
        db.session.commit()

        flash("Deck created successfully!", "success")
        return redirect(url_for('deck'))  # Redirect to deck listing page or appropriate route

    # Handle GET request to show the form
    cards = Cards.query.all()  # Fetch available cards to display in the form
    form = AddDeckForm()
    return render_template('add_deck.html', form=form, cards=cards)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    register_form = New_user()  # Also create an instance of the registration form

    if request.method == 'GET':
        print('GET')
        return render_template('login_signup.html', login_form=login_form, register_form=register_form)
    else:
        if login_form.validate_on_submit():
            print('validate login')
            user = User.query.filter_by(email=login_form.email.data).first()
            if user:
                if user.check_password(login_form.password.data):
                    print("check password")
                    session['user_id'] = user.id
                    flash(f'Welcome Back, {user.full_name}!', 'success')
                    return redirect(url_for('home'))  # Redirect after a successful login
                else:
                    print("wrong password")
                    flash('Invalid password. Please try again.', 'danger')
            else:
                print("email not found")
                flash('Email not found. Please signup.', 'danger')
        return render_template('login_signup.html', login_form=login_form, register_form=register_form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    register_form = New_user()
    login_form = LoginForm()

    if request.method == 'GET':
        print("get")
        return render_template('login_signup.html', login_form=login_form, register_form=register_form)

    # Handle POST request
    if register_form.validate_on_submit():
        print('validate register')
        new_user = models.User()
        new_user.full_name = register_form.full_name.data
        new_user.email = register_form.email.data
        new_user.set_password(register_form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

    # Handle case where form is not validated
    flash('Passwords entered might be incorrect. Please check!', 'danger')
    return render_template('login_signup.html', login_form=login_form, register_form=register_form)


@app.route("/logout")
def logout():
    if 'user_id' not in session:
        flash('You are not logged in', 'danger')
        return redirect(url_for('home'))
    else:
        session.pop('user_id', None)
        session.pop('user_name', None)
        return redirect(url_for('home'))


@app.route("/welcome")
def welcome():
    return render_template('welcome.html')


if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
