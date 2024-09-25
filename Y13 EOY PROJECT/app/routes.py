import os
from sqlalchemy.exc import IntegrityError
from flask import render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from app import app

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, "clash.db")
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
        # Increase by 10% per level
        multiplier = 1.1 ** (level - starting_level)
        levels.append({
            'level': level,
            'health': round(health * multiplier),
            'damage': round(damage * multiplier),
            'damage_per_sec': round(damage_per_sec * multiplier),
        })
    return levels


@app.before_request
def before_request():
    # Check if the user is logged in
    g.is_logged_in = 'user_id' in session

    if g.is_logged_in:
        # Fetch user from database using the user_id stored in session
        user = User.query.filter_by(id=session['user_id']).first()

        # Check if the user has admin privileges (permission == 1)
        g.is_admin = user.is_admin == 1 if user else False
    else:
        g.is_admin = False


@app.errorhandler(404)
def page_not_found(e):
    """Render a custom 404 error page"""
    return render_template('404.html', pagename="error"), 404


@app.route("/")
def home():
    """Render the home page"""
    return render_template("home.html", pagename="home")


@app.route("/about")
def about():
    """render about page"""
    return render_template("about.html")


@app.route('/card/<int:card_id>')
def show_card(card_id):
    """
    Fetches and displays a card with the given card_id.

    Parameters:
    card_id (int): The ID of the card to be displayed.

    Returns:
    Response: The rendered template showing the card details or a
    redirect if an error occurs.
    """
    try:
        # Ensure the card has permission 1
        card = models.Cards.\
            query.filter_by(id=card_id, pending=1).first_or_404()

        card_stats = models.Card_stats.query.filter_by(card_id=card_id).all()

        # Debug output to ensure stats are fetched
        print("Card:", card)
        print("Card Stats:", card_stats)

        return render_template('card.html', card=card, card_stats=card_stats)
    except OverflowError:
        flash("no card avaiable")
        return redirect(url_for("cards"))


@app.route('/cards')
def cards():
    """For the user to see all the cards in the game"""

    rarity_id = request.args.get('Rarity')
    target_id = request.args.get('Target')
    card_type_id = request.args.get('CardType')
    elixir_cost = request.args.get('Elixir')

    # Fetch valid rarity IDs dynamically
    valid_rarity_ids = {str(r.id) for r in Rarity.query.all()}

    # Fetch valid target IDs dynamically
    valid_target_ids = {str(t.id) for t in Targets.query.all()}

    # Fetch valid card type IDs dynamically
    valid_card_type_ids = {str(ct.id) for ct in Card_type.query.all()}

    # Fetch valid elixir costs dynamically
    elixir_costs = {str(card.elixir) for card in Cards.query.all()}
    max_elixir_cost = max(elixir_costs) if elixir_costs else 10

    # Validate rarity_id
    if rarity_id and rarity_id != 'all':
        if rarity_id not in valid_rarity_ids:
            flash('Invalid rarity selected', 'danger')
            return redirect(url_for('cards'))

    # Validate target_id
    if target_id and target_id != 'all':
        if target_id not in valid_target_ids:
            flash('Invalid target selected', 'danger')
            return redirect(url_for('cards'))

    # Validate card_type_id
    if card_type_id and card_type_id != 'all':
        if card_type_id not in valid_card_type_ids:
            flash('Invalid card type selected', 'danger')
            return redirect(url_for('cards'))

    # Validate elixir_cost
    if elixir_cost and elixir_cost != 'all':
        try:
            elixir_value = int(elixir_cost)
            if elixir_value > int(max_elixir_cost):
                flash(f'Elixir cost is too large, max allowed is {max_elixir_cost}.', 'danger')
                return redirect(url_for('cards'))
        except ValueError:
            flash('Invalid elixir cost', 'danger')
            return redirect(url_for('cards'))

    query = Cards.query.filter_by(pending=1)

    if rarity_id and rarity_id != 'all':
        query = query.filter(Cards.rarity == int(rarity_id))

    if target_id and target_id != 'all':
        query = query.filter(Cards.card_target.any(id=int(target_id)))

    if card_type_id and card_type_id != 'all':
        query = query.filter(Cards.card_type == int(card_type_id))

    if elixir_cost and elixir_cost != 'all':
        query = query.filter(Cards.elixir == int(elixir_cost))

    all_cards = query.all()
    rarity = Rarity.query.order_by(Rarity.type).all()
    attack_type = Targets.query.order_by(Targets.target).all()
    card_types = Card_type.query.order_by(Card_type.type).all()
    elixir_costs = sorted({card.elixir for card in Cards.query.all()})

    if not all_cards:
        flash('No cards available in the database', 'danger')
        return redirect(url_for('cards'))

    return render_template('cards.html', cards=all_cards, rarity=rarity,
                           attack_type=attack_type, card_types=card_types,
                           elixir_costs=elixir_costs)


@app.route('/deck')
def deck():
    """ For user to see all the battle decks """
    user_id = request.args.get('User')

    # Fetch valid user IDs dynamically
    valid_user_ids = {str(u.id) for u in User.query.all()}

    # Validate user_id
    if user_id and user_id != 'all':
        if user_id not in valid_user_ids:
            flash('Invalid user selected', 'danger')
            return redirect(url_for('deck'))

    # Base query for decks
    query = Deck.query.join(User)

    # Filter by user if provided and valid
    if user_id and user_id != 'all':
        query = query.filter(Deck.user_id == int(user_id))

    decks = query.all()

    deck_data = []

    for new_deck in decks:
        # Extract card attributes from the deck
        all_cards = [
            new_deck.card1, new_deck.card2, new_deck.card3, new_deck.card4,
            new_deck.card5, new_deck.card6, new_deck.card7, new_deck.card8
        ]
        # Calculate average elixir cost
        total_elixir = 0
        count = 0
        for card in all_cards:
            if card and card.elixir:
                try:
                    # Convert the elixir cost to a float,
                    # in case it is stored as a string.
                    elixir_cost = float(card.elixir)
                    # Add the elixir cost to the total elixir sum.
                    total_elixir += elixir_cost
                    # Increment the count of valid elixir costs for averaging.
                    count += 1
                except ValueError:
                    # If the elixir cost cannot be converted to a float
                    # (invalid data)ignore that card and
                    # continue with the others.
                    pass
# Calculate the average elixir cost if there were any valid elixir values.
# If no valid elixir costs were found,
# set the average to 0 to avoid division by zero.
        average_elixir = total_elixir / count if count > 0 else 0

        # Store the deck and its related data, including the user
        deck_data.append({
            'cards': all_cards,
            'average_elixir': average_elixir,
            'user': new_deck.user
        })

    users = User.query.order_by(User.full_name).all()
    decks = query.all()
    print(decks)
    if not decks:
        flash('No Deck For User', 'danger')
        print("works")
        return redirect(url_for('deck'))

    return render_template('deck.html', deck_data=deck_data,
                           users=users, selected_user=user_id)


@app.route("/admin")
def admin():
    """Takes you to the admin page only if the user is an admin."""

    if 'user_id' not in session:
        flash("You must be logged in to access this page.", 'error')
        return redirect(url_for('login'))
# makeing sure that the user logged in is the admin
    user = models.User.query.get(session['user_id'])
    if not user or user.is_admin != 1:
        return redirect(url_for('home'))

    pending_cards = models.Cards.query.filter_by(pending=0).all()
    return render_template("admin.html", pending_cards=pending_cards)


@app.route("/admin/approve_card/<int:approve_id>")
def approve(approve_id):

    """here the admin is able to accept the card that a user
    is wanting to add into the database, it will change the number in
    the pending coloumn from a 0 to 1 and then will be able to see the card
    in the all cards page"""

    if 'user_id' not in session or session.get('user_id') != 7:
        flash("Admin access only", 'error')
        return redirect(url_for('home'))
    else:
        pending_card = models.Cards.query.get_or_404(approve_id)
        # Approve the card
        pending_card.pending = 1
        db.session.add(pending_card)
        db.session.commit()
        flash("Card and its Evolution (if any) have been approved", "success")
        return redirect(url_for("admin"))


@app.route("/admin/reject_card/<int:reject_id>")
def reject(reject_id):

    """Admin is able to reject a card the user has added"""

    if 'user_id' not in session or session.get('user_id') != 7:
        flash("Admin access only", 'error')
        return redirect(url_for('home'))

    # Fetch the card to delete
    card_to_delete = models.Cards.query.get_or_404(reject_id)

    # Check if the card has an associated evolution
    if card_to_delete.evolution:
        # Fetch the evolution to delete
        evolution_to_delete = models.Evolution.\
                            query.get(card_to_delete.evolution)
        if evolution_to_delete:
            db.session.delete(evolution_to_delete)

    if card_to_delete.special:
        # Ensure card_to_delete.special is an integer ID
        special_id = card_to_delete.special if\
              isinstance(card_to_delete.special, int) \
              else card_to_delete.special.id
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

    """the user is able to add new cards to the database"""

    if 'user_id' not in session:
        flash('You need to be logged in to add a card.', 'danger')
        return redirect(url_for("login"))
# to return the different forms to one page
    form = Add_Card()
    evolution_form = Add_Evolution()
    card_stats_form = Add_card_stats()
    special_form = Add_Special()

    target = models.Targets.query.all()
    target_list = []
    for t in target:
        target_list.append(t.target)
    if form.validate_on_submit() and \
            card_stats_form.validate_on_submit() and \
            'submit_card_and_stats' in request.form:
        new_card = models.Cards()
        new_card.name = form.name.data.capitalize()
        new_card.description = form.description.data
        new_card.rarity = form.rarity.data
        new_card.Min_trophies_unlocked = form.trophies.data
        new_card.speed = form.speed.data
        new_card.card_type = form.card_type.data
        new_card.elixir = form.elixir.data

        if form.special.data != 0:
            new_card.Special = form.special.data
        else:
            new_card.Special = None

        if form.evolution.data != 0:
            new_card.evolution = form.evolution.data
        else:
            new_card.evolution = None

        # Handle many-to-many relationship for card_target
        target_ids = form.target.data
        targets = models.Targets.query.\
            filter(models.Targets.id.in_(target_ids)).all()
        new_card.card_target = targets  # type:ignore

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
                return redirect(url_for('home'))

        except IntegrityError:
            db.session.rollback()
            flash("Card with this name already exists. Please choose a different name.", 'danger')

    return render_template('add_card.html', form=form,
                           evolution_form=evolution_form,
                           card_stats_form=card_stats_form,
                           special_form=special_form,
                           target_list=target_list,
                           title="Add Card")


@app.route('/add_special', methods=['GET', 'POST'])
def add_special():

    """The user is able to add a special ablity for champion cards"""
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("login"))
# to return the different forms to one page
    evolution_form = Add_Evolution()
    form = Add_Card()
    special_form = Add_Special()

    if 'submit_special' in request.form and special_form.validate_on_submit():
        new_special = models.Special()
        new_special.name = special_form.name.data.capitalize()
        new_special.activation_elixir = special_form.elixir.data
        new_special.description = special_form.description.data
        try:
            db.session.add(new_special)
            db.session.commit()
            flash("Special ablity added, go back to add cards")
        except IntegrityError:
            db.session.rollback()
            flash("Special ability already in the database")
    return render_template("add_card.html", form=form,
                           evolution_form=evolution_form,
                           special_form=special_form,
                           title="Add Special")


@app.route("/add_evolution", methods=['GET', 'POST'])
def add_evolution():
    """user is able to add evolutions for a card"""
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("login"))
# to return the different forms to one page
    evolution_form = Add_Evolution()
    form = Add_Card()
    special_form = Add_Special()

    if 'submit_evolution' in request.form and\
            evolution_form.validate_on_submit():
        new_evolution = models.Evolution()
        new_evolution.cycle_for = evolution_form.cycle_for.data.capitalize()
        new_evolution.cycles = evolution_form.cycles.data
        new_evolution.stat_boost = evolution_form.stat_boost.data
        new_evolution.special_ability = evolution_form.special_ability.data

        try:
            db.session.add(new_evolution)
            db.session.commit()
            flash("Evolution added")
        except IntegrityError:
            db.session.rollback()
            flash('Evolution with this type already exists. Please choose a different type.', 'danger')

    return render_template('add_card.html', evolution_form=evolution_form,
                           special_form=special_form,
                           form=form, title="Add Evolution")


@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck():
    """ Check if user is logged in"""
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
                else:
                    flash(f"Card with ID {card_id} not found.", "danger")
                    return redirect(url_for('add_deck'))

        # Ensure at least 8 cards are selected
        if len(deck_cards) < 8:
            flash("Fill out all the card slots before submitting.", "danger")
            print("works")
            return redirect(url_for('add_deck'))

        # Check if the first card has an evolution and use its image
        card1 = deck_cards[0] if len(deck_cards) > 0 else None
        if card1 and card1.evolution:
            evolution_image = card1.evo.image_evo
            flash(f"Using evolution image: {evolution_image}", "info")

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
        return redirect(url_for('deck'))

    # Handle GET request to show the form
    new_card = Cards.query.all()
    form = AddDeckForm()
    return render_template('add_deck.html', form=form, cards=new_card)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    register_form = New_user()

    if request.method == 'GET':
        print('GET')
        return render_template('login_signup.html', login_form=login_form,
                               register_form=register_form)
    else:
        if login_form.validate_on_submit():
            print('validate login')
            user = User.query.filter_by(email=login_form.email.data).first()
            if user:
                if user.check_password(login_form.password.data):
                    print("check password")
                    session['user_id'] = user.id
                    flash(f'Welcome Back, {user.full_name}!', 'success')
                    return redirect(url_for('home'))
                else:
                    print("wrong password")
                    flash('Invalid password. Please try again.', 'danger')
            else:
                print("email not found")
                flash('Email not found. Please signup.', 'danger')
        return render_template('login_signup.html', login_form=login_form,
                               register_form=register_form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    register_form = New_user()
    login_form = LoginForm()

    if request.method == 'GET':
        print("get")
        return render_template('login_signup.html', login_form=login_form,
                               register_form=register_form)

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
    return render_template('login_signup.html', login_form=login_form,
                           register_form=register_form)


@app.route("/logout")
def logout():
    if 'user_id' not in session:
        flash('You are not logged in', 'danger')
        return redirect(url_for('home'))
    else:
        session.pop('user_id', None)
        session.pop('user_name', None)
        return redirect(url_for('home'))


if __name__ == "__main__":  # type:ignore
    app.run(debug=True)
