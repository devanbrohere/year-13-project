from app import app
from sqlalchemy.exc import IntegrityError
from flask import render_template, abort, request, redirect, url_for, flash, session, jsonify
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


@app.route('/cards')
def cards():
    rarity_id = request.args.get('Rarity')
    target_id = request.args.get('Target')
    type_id = request.args.get('Cardype')

    query = models.Cards.query

    if rarity_id and rarity_id != 'all':
        query = query.filter(models.Cards.rarity == rarity_id)

    if target_id and target_id != 'all':
        query = query.filter(models.Cards.card_target.any(id=target_id))

    if type_id and type_id != 'all':
        query = query.filter(models.Cards.card_type.any(id=type_id))

    cards = query.all()
    rarity = Rarity.query.order_by(Rarity.type).all()
    attack_type = Targets.query.order_by(Targets.target).all()
    card_type = Card_type.query.order_by(Card_type.type).all()

    if not cards:
        flash('No cards available in the database', 'danger')
        return redirect(url_for('cards'))
    
    return render_template('cards.html', cards=cards, rarity=rarity, attack_type=attack_type, card_type=card_type)


@app.route('/card/<int:id>')
def card(id):
    card = models.Cards.query.filter_by(id=id).first()
    if card is None:
        flash('Card not in database', 'danger')
        return redirect(url_for('cards'))  
    return render_template('card.html', card=card)


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("home"))

    form = Add_Card()
    evolution_form = Add_Evolution()
    stats_form = Add_card_stats()

    # Initialize card_stat as None
    card_stat = None

    # Handle Card form submission
    if form.validate_on_submit() and 'submit_card' in request.form:
        new_card = models.Cards()
        new_card.name = form.name.data.capitalize()
        new_card.description = form.description.data
        new_card.rarity = form.rarity.data
        new_card.Min_trophies_unlocked = form.trophies.data
        new_card.evolution = form.evolution.data
        new_card.speed = form.speed.data
        new_card.Special = form.special.data
        new_card.card_type = form.card_type.data
        new_card.spawn_time = form.spawn_time.data
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
            return redirect(url_for('details', ref=new_card.id))
        except IntegrityError:
            db.session.rollback()
            flash('Card with this name already exists. Please choose a different name.', 'danger')

    if stats_form.validate_on_submit() and 'submit_stats' in request.form:
        # Determine rarity and level range
        rarity = form.rarity.data
        if rarity == 'Common':
            level_start = 1
            level_end = 15
        elif rarity == 'Rare':
            level_start = 5
            level_end = 15
        elif rarity in ['Epic', 'Legendary']:
            level_start = 11
            level_end = 15
        else:
            flash('Unknown rarity type.', 'danger')
            return redirect(url_for('add_card'))

        # Calculate and add card stats for each level within the determined range
        for level in range(level_start, level_end + 1):
            health_value = stats_form.health.data * (1 + 0.10 * (level - level_start))
            damage_value = stats_form.damage.data * (1 + 0.10 * (level - level_start))
            damage_sec_value = stats_form.damage_sec.data * (1 + 0.10 * (level - level_start))

            card_stat = models.Card_stats()
            card_stat.card_id = new_card.id
            card_stat.health = health_value
            card_stat.level = level
            card_stat.damage = damage_value
            card_stat.damage_per_sec = damage_sec_value
            try:
                db.session.add(card_stat)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while saving card stats.', 'danger')
                return redirect(url_for('add_card'))

        return redirect(url_for('details', ref=new_card.id))

    if evolution_form.validate_on_submit() and 'submit_evolution' in request.form:
        new_evolution = models.Evolution()
        new_evolution.cycle_for = evolution_form.cycle_for.data
        new_evolution.cycles = evolution_form.cycles.data
        new_evolution.stat_boost = evolution_form.stat_boost.data
        new_evolution.special_ability = evolution_form.special_ability.data

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
            return redirect(url_for('details', ref=new_evolution.id))
        except IntegrityError:
            db.session.rollback()
            flash('Evolution with this type already exists. Please choose a different type.', 'danger')

    return render_template('add_card.html', form=form, evolution_form=evolution_form, stats_form=stats_form, card_stat=card_stat, title="Add Card and Evolution")




@app.route('/details/<int:ref>')
def details(ref):
    deets = models.Cards.query.filter_by(id=ref).first_or_404()
    return render_template("card.html", card=deets, title=deets.name)


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
