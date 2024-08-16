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
from app.models import Cards, User, Rarity, Targets
from app.forms import Add_Card, New_user, LoginForm, Add_Evolution, Add_Rarity, Add_Special, Add_Target, Add_Trophies

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
    cards = models.Cards.query.all()
    rarity = Rarity.query.order_by(Rarity.type).all()
    attack_type = Targets.query.order_by(Targets.target).all()
    if not cards:
        flash('No cards available in the database', 'danger')
        return redirect(url_for('some_other_route'))  # Redirect to a different page, or you can render a specific template
    return render_template('cards.html', cards=cards, rarity=rarity, attack_type=attack_type)

@app.route("/api/cards", methods=['GET'])
def filter_cards():
    rarity_id =  request.args.get('Rarity')
    target_id = request.args.get('Target')
    query = models.Cards.query
    if rarity_id and rarity_id != 'all':
        query = query.filter(models.Cards.rarity == rarity_id)
    if target_id and target_id != 'all':
        query = query.filter(models.Cards.card_target.any(id=target_id))
    cards = query.all()
    cards_list = [{'id': card.id, "name":card.name, "image": card.image} for card in cards]
    return jsonify({"cards": cards_list})



@app.route('/card/<int:id>')
def card(id):
    card = models.Cards.query.filter_by(id=id).first()
    if card is None:
        flash('Card not in database', 'danger')
        return redirect(url_for('cards'))  # Redirecting to the list of all cards, or any other page you prefer
    return render_template('card.html', card=card)


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    if 'user_id' not in session:
        flash('Please login', 'danger')
        return redirect(url_for("home"))
    else:
        form = Add_Card()

        if request.method == "POST":
            if form.validate_on_submit():
                # Create a new card instance
                new_card = models.Cards()
                new_card.name = form.name.data
                new_card.description = form.description.data
                new_card.rarity = form.rarity.data
                new_card.Min_trophies_unlocked = form.trophies.data
                new_card.evolution = form.evolution.data
                new_card.speed = form.speed.data
                new_card.Special = form.special.data
                new_card.spawn_time = form.spawn_time.data
                new_card.elixir = form.elixir.data
                
                # Handle many-to-many relationship for card_target
                target_ids = form.target.data  # list of selected target ids
                targets = models.Targets.query.filter(models.Targets.id.in_(target_ids)).all()
                new_card.card_target = targets  # Associate targets with the card

                # Handle file upload
                if form.image.data:
                    filename = secure_filename(form.image.data.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Ensure the upload folder exists
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])

                    # Save the file
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
                    return render_template('add_card.html', form=form, title="Add A Card")

            else:
                flash("Form validation failed. Please correct the errors and try again.", 'danger')
                return render_template('add_card.html', form=form, title="Add A Card")

        return render_template("add_card.html", form=form, title="Add A Card")


@app.route("/add_rarity", methods=['GET', 'POST'])
def add_rarity():
    if 'user_id' not in session:
            flash('Please login', 'danger')
            return redirect(url_for("home"))
    else:
        rarity_form = Add_Rarity
        if request.method == 'POST':
            if rarity_form.validate_on_submit():
                new_rarity = models.Rarity()
                new_rarity.rarity= rarity_form.rarity.data
                
                try:
                    db.session.add(new_rarity)
                    db.session.commit()
                    return redirect(url_for('details', ref=new_rarity.id))
                except IntegrityError:
                    db.session.rollback()
                    flash('Card with this name already exists. Please choose a different name.', 'danger')
                    return render_template('add_card.html', rarity_form=rarity_form, title="Add A Card")
            else:
                flash("Form validation failed. Please correct the errors and try again.", 'danger')
                return render_template('add_card.html', rarity_form=rarity_form, title="Add A Card")
        return render_template("add_card.html", rarity_form=rarity_form, title="Add A Card")


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
            if user and user.check_password(login_form.password.data):
                print("check password")
                session['user_id'] = user.id
                flash(f'Welcome Back, {user.full_name}!', 'success')
                return redirect(url_for('welcome'))  # Assuming you want to redirect after a successful login
            else:
                print("wrong password")
                flash('Invalid email or password.', 'danger')
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
