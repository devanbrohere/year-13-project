from app import app
from sqlalchemy.exc import IntegrityError
from flask import render_template, abort, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
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
from app.models import Cards, User, Rarity, Targets, Card_type
from app.forms import Add_Card, New_user, LoginForm, Add_Evolution, Add_Rarity, Add_Special, Add_Target, Add_Trophies, Add_card_stats


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
    card = models.Cards.query.get(id)
    card_stats = models.Card_stats.query.filter_by(card_id=id).all()
    print("Card:", card)
    print("Card Stats:", card_stats)  # Debug output to ensure stats are fetched
    return render_template('card.html', card=card, card_stats=card_stats)



@app.route('/cards')
def cards():
    rarity_id = request.args.get('Rarity')
    target_id = request.args.get('Target')
    card_type_id = request.args.get('CardType')

    query = Cards.query

    if rarity_id and rarity_id != 'all':
        query = query.filter(Cards.rarity == int(rarity_id))  # Ensure you're filtering by integer

    if target_id and target_id != 'all':
        query = query.filter(Cards.card_target.any(id=int(target_id)))  # Ensure you're filtering by integer

    if card_type_id and card_type_id != 'all':
        query = query.filter(Cards.card_type == int(card_type_id))  # Ensure you're filtering by integer

    cards = query.all()
    rarity = Rarity.query.order_by(Rarity.type).all()
    attack_type = Targets.query.order_by(Targets.target).all()
    card_types = Card_type.query.order_by(Card_type.type).all()

    if not cards:
        flash('No cards available in the database', 'danger')
        return redirect(url_for('cards'))

    return render_template('cards.html', cards=cards, rarity=rarity, attack_type=attack_type, card_types=card_types)


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("home"))

    form = Add_Card()
    evolution_form = Add_Evolution()
    card_stats_form = Add_card_stats()

    if form.validate_on_submit() and card_stats_form.validate_on_submit() and 'submit_card_and_stats' in request.form:
        new_card = models.Cards()
        new_card.name = form.name.data.capitalize()
        new_card.description = form.description.data
        new_card.rarity = form.rarity.data
        new_card.Min_trophies_unlocked = form.trophies.data
        new_card.evolution = form.evolution.data
        new_card.speed = form.speed.data
        new_card.Special = form.special.data
        new_card.card_type = form.card_type.data
        new_card.elixir = form.elixir.data

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
            levels = calculate_levels(starting_level, card_stats_form.health.data, card_stats_form.damage.data, card_stats_form.damage_sec.data)

            for level_data in levels:
                card_stat = models.Card_stats()
                card_stat.card_id = new_card.id
                card_stat.level = level_data['level']
                card_stat.health = level_data['health']
                card_stat.damage = level_data['damage']
                card_stat.damage_per_sec = level_data['damage_per_sec']
                db.session.add(card_stat)
            
            db.session.commit()
            return redirect(url_for('card', ref=new_card.id))
        except IntegrityError:
            db.session.rollback()
            flash('Card with this name already exists. Please choose a different name.', 'danger')

    return render_template('add_card.html', form=form, evolution_form=evolution_form, card_stats_form=card_stats_form, title="Add Card")


@app.route("/add_evolution", methods=['GET', 'POST'])
def add_evolution():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("home"))

    evolution_form = Add_Evolution()
    form = Add_Card()

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
            return redirect(url_for('card', ref=new_evolution.id))
        except IntegrityError:
            db.session.rollback()
            flash('Evolution with this type already exists. Please choose a different type.', 'danger')

    return render_template('add_card.html', evolution_form=evolution_form, form=form, title="Add Evolution")


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
